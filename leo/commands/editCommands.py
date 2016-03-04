# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514035813.1: * @file ../commands/editCommands.py
#@@first
'''Leo's general editing commands.'''
#@+<< imports >>
#@+node:ekr.20150514050149.1: ** << imports >> (editCommands.py)
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
import os
import re
#@-<< imports >>

def cmd(name):
    '''Command decorator for the EditCommandsClass class.'''
    return g.new_cmd_decorator(name, ['c', 'editCommands',])

class EditCommandsClass(BaseEditCommandsClass):
    '''Editing commands with little or no state.'''
    # pylint: disable=eval-used
    #@+others
    #@+node:ekr.20150514063305.116: ** ctor (EditCommandsClass)
    def __init__(self, c):
        '''Ctor for EditCommandsClass class.'''
        # pylint: disable=super-init-not-called
        self.c = c
        self.ccolumn = '0' # For comment column functions.
        self.extendMode = False # True: all cursor move commands extend the selection.
        self.fillPrefix = '' # For fill prefix functions.
        self.fillColumn = 0 # For line centering.
            # Set by the set-fill-column command.
            # If zero, @pagewidth value is used.
        self.moveSpotNode = None # A VNode.
        self.moveSpot = None # For retaining preferred column when moving up or down.
        self.moveCol = None # For retaining preferred column when moving up or down.
        self.sampleWidget = None # Created later.
        self.swapSpots = []
        self._useRegex = False # For replace-string
        self.w = None # For use by state handlers.
        # Settings...
        cf = c.config
        self.autocompleteBrackets = cf.getBool('autocomplete-brackets')
        self.bracketsFlashBg = cf.getColor('flash-brackets-background-color')
        self.bracketsFlashCount = cf.getInt('flash-brackets-count')
        self.bracketsFlashDelay = cf.getInt('flash-brackets-delay')
        self.bracketsFlashFg = cf.getColor('flash-brackets-foreground-color')
        self.flashMatchingBrackets = cf.getBool('flash-matching-brackets')
        self.smartAutoIndent = cf.getBool('smart_auto_indent')
        self.openBracketsList = cf.getString('open_flash_brackets') or '([{'
        self.closeBracketsList = cf.getString('close_flash_brackets') or ')]}'
        self.initBracketMatcher(c)
    #@+node:ekr.20150514063305.118: ** doNothing
    @cmd('do-nothing')
    def doNothing(self, event):
        '''A placeholder command, useful for testing bindings.'''
        pass
    #@+node:ekr.20150514063305.121: ** c/ts/toPY
    #@+<< theory of operation >>
    #@+node:ekr.20150514063305.122: *3* << theory of operation >>
    #@@nocolor
    #@+at
    # 
    # 1. We use a single list, aList, for all changes to the text. This reduces
    #    stress on the gc. All replacesments are done **in place** in aList.
    # 
    # 2. The following pattern ensures replacements do not happen in strings and comments::
    # 
    #     def someScan(self,aList):
    #         i = 0
    #         while i < len(aList):
    #             if self.is_string_or_comment(aList,i):
    #                 i = skip_string_or_comment(aList,i)
    #             elif < found what we are looking for >:
    #                 <convert what we are looking for, setting i>
    #             else: i += 1
    #@-<< theory of operation >>
    #@+<< class To_Python >>
    #@+node:ekr.20150514063305.123: *3* << class To_Python >>
    class To_Python:
        '''The base class for x-to-python commands.'''
        #@+others
        #@+node:ekr.20150514063305.124: *4* top.cmd (decorator
        #@+node:ekr.20150514063305.125: *4* ctor (To_Python)
        def __init__(self, c):
            '''Ctor for To_Python class.'''
            self.c = c
            self.p = self.c.p.copy()
            aList = g.get_directives_dict_list(self.p)
            self.tab_width = g.scanAtTabwidthDirectives(aList) or 4
        #@+node:ekr.20150514063305.126: *4* go
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
        #@+node:ekr.20150514063305.127: *4* convertCodeList (must be defined in subclasses)
        def convertCodeList(self, aList):
            '''The main search/replace method.'''
            g.trace('must be defined in subclasses.')
        #@+node:ekr.20150514063305.128: *4* Utils
        #@+node:ekr.20150514063305.129: *5* match...
        #@+node:ekr.20150514063305.130: *6* match
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
        #@+node:ekr.20150514063305.131: *6* match_word
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
        #@+node:ekr.20150514063305.132: *5* insert_not
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
        #@+node:ekr.20150514063305.133: *5* is...
        #@+node:ekr.20150514063305.134: *6* is_section_def/ref
        def is_section_def(self, p):
            return self.is_section_ref(p.h)

        def is_section_ref(self, s):
            n1 = s.find("<<", 0)
            n2 = s.find(">>", 0)
            return -1 < n1 < n2 and s[n1 + 2: n2].strip()
        #@+node:ekr.20150514063305.135: *6* is_string_or_comment
        def is_string_or_comment(self, s, i):
            # Does range checking.
            m = self.match
            return m(s, i, "'") or m(s, i, '"') or m(s, i, "//") or m(s, i, "/*")
        #@+node:ekr.20150514063305.136: *6* is_ws and is_ws_or_nl
        def is_ws(self, ch):
            return ch in ' \t'

        def is_ws_or_nl(self, ch):
            return ch in ' \t\n'
        #@+node:ekr.20150514063305.137: *5* prevNonWsChar and prevNonWsOrNlChar
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
        #@+node:ekr.20150514063305.138: *5* remove...
        #@+node:ekr.20150514063305.139: *6* removeBlankLines
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
        #@+node:ekr.20150514063305.140: *6* removeExcessWs
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
        #@+node:ekr.20150514063305.141: *6* removeExessWsFromLine
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
        #@+node:ekr.20150514063305.142: *6* removeMatchingBrackets
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
        #@+node:ekr.20150514063305.143: *6* removeSemicolonsAtEndOfLines
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
        #@+node:ekr.20150514063305.144: *6* removeTrailingWs
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
        #@+node:ekr.20150514063305.145: *5* replace... & safe_replace
        #@+node:ekr.20150514063305.146: *6* replace
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
        #@+node:ekr.20150514063305.147: *6* replaceComments
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
        #@+node:ekr.20150514063305.148: *7* munge_block_comment
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
        #@+node:ekr.20150514063305.149: *6* replaceSectionDefs
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
        #@+node:ekr.20150514063305.150: *6* safe_replace
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
        #@+node:ekr.20150514063305.151: *5* skip
        #@+node:ekr.20150514063305.152: *6* skip_c_block_comment
        def skip_c_block_comment(self, s, i):
            assert(self.match(s, i, "/*"))
            i += 2
            while i < len(s):
                if self.match(s, i, "*/"):
                    return i + 2
                else:
                    i += 1
            return i
        #@+node:ekr.20150514063305.153: *6* skip_line
        def skip_line(self, s, i):
            while i < len(s) and s[i] != '\n':
                i += 1
            return i
        #@+node:ekr.20150514063305.154: *6* skip_past_line
        def skip_past_line(self, s, i):
            while i < len(s) and s[i] != '\n':
                i += 1
            if i < len(s) and s[i] == '\n':
                i += 1
            return i
        #@+node:ekr.20150514063305.155: *6* skip_past_word
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
        #@+node:ekr.20150514063305.156: *6* skip_string
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
        #@+node:ekr.20150514063305.157: *6* skip_string_or_comment
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
        #@+node:ekr.20150514063305.158: *6* skip_to_matching_bracket
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
        #@+node:ekr.20150514063305.159: *6* skip_ws and skip_ws_and_nl
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
    #@+<< class C_To_Python (To_Python) >>
    #@+node:ekr.20150514063305.160: *3* << class C_To_Python (To_Python) >>
    class C_To_Python(To_Python):
        #@+others
        #@+node:ekr.20150514063305.161: *4* ctor & helpers (C_To_Python)
        def __init__(self, c):
            '''Ctor for C_To_Python class.'''
            # pylint: disable=super-init-not-called
            c.editCommands.To_Python.__init__(self, c)
                # init the base class
            # Internal state...
            self.class_name = ''
                # The class name for the present function.  Used to modify ivars.
            self.ivars = []
                # List of ivars to be converted to self.ivar
            self.get_user_types()
        #@+node:ekr.20150514063305.162: *5* get_user_types
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
        #@+node:ekr.20150514063305.163: *5* parse_ivars_data
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
        #@+node:ekr.20150514063305.164: *4* convertCodeList (C_To_Python) & helpers
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
        #@+node:ekr.20150514063305.165: *5* handle_all_keywords
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
        #@+node:ekr.20150514063305.166: *6* handle_keyword
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
        #@+node:ekr.20150514063305.167: *5* mungeAllFunctions
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
        #@+node:ekr.20150514063305.168: *6* handlePossibleFunctionHeader
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
        #@+node:ekr.20150514063305.169: *6* massageFunctionArgs
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
        #@+node:ekr.20150514063305.170: *6* massageFunctionHead (sets .class_name)
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
        #@+node:ekr.20150514063305.171: *6* massageFunctionBody & helpers
        def massageFunctionBody(self, body):
            body = self.massageIvars(body)
            body = self.removeCasts(body)
            body = self.removeTypeNames(body)
            body = self.dedentBlocks(body)
            return body
        #@+node:ekr.20150514063305.172: *7* dedentBlocks
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
        #@+node:ekr.20150514063305.173: *7* massageIvars
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
        #@+node:ekr.20150514063305.174: *7* removeCasts
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
        #@+node:ekr.20150514063305.175: *7* removeTypeNames
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
    #@-<< class C_To_Python (To_Python) >>
    #@+<< class TS_To_Python (To_Python) >>
    #@+node:ekr.20150514063305.176: *3* << class TS_To_Python (To_Python) >>
    class TS_To_Python(To_Python):
        #@+others
        #@+node:ekr.20150514063305.177: *4* ctor (TS_To_Python)
        def __init__(self, c):
            '''Ctor for TS_To_Python class.'''
            # pylint: disable=super-init-not-called
            c.editCommands.To_Python.__init__(self, c)
                # init the base class
            self.class_name = ''
                # The class name for the present function.  Used to modify ivars.
        #@+node:ekr.20150514063305.178: *4* convertCodeList (TS_To_Python) & helpers
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
        #@+node:ekr.20150514063305.179: *5* comment_scope_ids
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
        #@+node:ekr.20150514063305.180: *6* handle_scope_keyword
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
        #@+node:ekr.20150514063305.181: *5* handle_all_keywords
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
        #@+node:ekr.20150514063305.182: *6* handle_keyword
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
        #@+node:ekr.20150514063305.183: *5* mungeAllClasses
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
        #@+node:ekr.20150514063305.184: *5* mungeAllFunctions & helpers
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
        #@+node:ekr.20150514063305.185: *6* handlePossibleFunctionHeader
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
        #@+node:ekr.20150514063305.186: *6* massageFunctionArgs
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
        #@+node:ekr.20150514063305.187: *6* massageFunctionHead (sets .class_name)
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
        #@+node:ekr.20150514063305.188: *6* massageFunctionBody & helper
        def massageFunctionBody(self, body):
            # body = self.massageIvars(body)
            # body = self.removeCasts(body)
            # body = self.removeTypeNames(body)
            body = self.dedentBlocks(body)
            return body
        #@+node:ekr.20150514063305.189: *7* dedentBlocks
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
    #@-<< class TS_To_Python (To_Python) >>

    @cmd('c-to-python')
    def cToPy(self, event):
        '''
        The c-to-python command converts c or c++ text to python text.
        The conversion is not perfect, but it eliminates a lot of tedious
        text manipulation.
        '''
        self.C_To_Python(self.c).go()
        self.c.bodyWantsFocus()

    @cmd('typescript-to-py')
    def tsToPy(self, event):
        '''
        The typescript-to-python command converts typescript text to python
        text. The conversion is not perfect, but it eliminates a lot of tedious
        text manipulation.
        '''
        # Compiler stats: 35 files, 1489 nodes, 100 to 120 sec.
        self.TS_To_Python(self.c).go()
        self.c.bodyWantsFocus()
    #@+node:ekr.20150514063305.190: ** cache (leoEditCommands)
    @cmd('clear-all-caches')
    def clearAllCaches(self, event=None):
        '''Clear all of Leo's file caches.'''
        c = self.c
        if c.cacher:
            c.cacher.clearAllCaches()

    @cmd('clear-cache')
    def clearCache(self, event=None):
        '''Clear the outline's file cache.'''
        c = self.c
        if c.cacher:
            c.cacher.clearCache()
    #@+node:ekr.20150514063305.191: ** capitalization & case
    #@+node:ekr.20150514063305.192: *3* capitalizeWord & up/downCaseWord
    @cmd('capitalize-word')
    def capitalizeWord(self, event):
        '''Capitalize the word at the cursor.'''
        self.capitalizeHelper(event, 'cap', 'capitalize-word')

    @cmd('downcase-word')
    def downCaseWord(self, event):
        '''Convert all characters of the word at the cursor to lower case.'''
        self.capitalizeHelper(event, 'low', 'downcase-word')

    @cmd('upcase-word')
    def upCaseWord(self, event):
        '''Convert all characters of the word at the cursor to UPPER CASE.'''
        self.capitalizeHelper(event, 'up', 'upcase-word')
    #@+node:ekr.20150514063305.194: *3* capitalizeHelper
    def capitalizeHelper(self, event, which, undoType):
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getWord(s, ins)
        word = s[i: j]
        if not word.strip():
            return
        self.beginCommand(w, undoType=undoType)
        if which == 'cap': word2 = word.capitalize()
        elif which == 'low': word2 = word.lower()
        elif which == 'up': word2 = word.upper()
        else: g.trace('can not happen: which = %s' % s(which))
        changed = word != word2
        if changed:
            w.delete(i, j)
            w.insert(i, word2)
            w.setSelectionRange(ins, ins, insert=ins)
        self.endCommand(changed=changed, setLabel=True)
    #@+node:ekr.20150514063305.195: ** clicks and focus (EditCommandsClass)
    #@+node:ekr.20150514063305.196: *3* activate-x-menu & activateMenu (EditCommandsClass)
    @cmd('activate-cmds-menu')
    def activateCmdsMenu(self, event=None):
        '''Activate Leo's Cmnds menu.'''
        self.activateMenu('Cmds')

    @cmd('activate-edit-menu')
    def activateEditMenu(self, event=None):
        '''Activate Leo's Edit menu.'''
        self.activateMenu('Edit')

    @cmd('activate-file-menu')
    def activateFileMenu(self, event=None):
        '''Activate Leo's File menu.'''
        self.activateMenu('File')

    @cmd('activate-help-menu')
    def activateHelpMenu(self, event=None):
        '''Activate Leo's Help menu.'''
        self.activateMenu('Help')

    @cmd('activate-outline-menu')
    def activateOutlineMenu(self, event=None):
        '''Activate Leo's Outline menu.'''
        self.activateMenu('Outline')

    @cmd('activate-plugins-menu')
    def activatePluginsMenu(self, event=None):
        '''Activate Leo's Plugins menu.'''
        self.activateMenu('Plugins')

    @cmd('activate-window-menu')
    def activateWindowMenu(self, event=None):
        '''Activate Leo's Window menu.'''
        self.activateMenu('Window')

    def activateMenu(self, menuName):
        c = self.c
        c.frame.menu.activateMenu(menuName)
    #@+node:ekr.20150514063305.197: *3* cycleFocus
    @cmd('cycle-focus')
    def cycleFocus(self, event):
        '''Cycle the keyboard focus between Leo's outline, body and log panes.'''
        c, k = self.c, self.c.k
        w = event and event.widget
        body = c.frame.body.wrapper
        log = c.frame.log.logCtrl
        tree = c.frame.tree.canvas
        # A hack for the Qt gui.
        if hasattr(w, 'logCtrl'):
            w = w.logCtrl
        panes = [body, log, tree]
        # g.trace(w in panes,event.widget,panes)
        if w in panes:
            i = panes.index(w) + 1
            if i >= len(panes): i = 0
            pane = panes[i]
        else:
            pane = body
        # Warning: traces mess up the focus
        # g.pr(g.app.gui.widget_name(w),g.app.gui.widget_name(pane))
        # This works from the minibuffer *only* if there is no typing completion.
        c.widgetWantsFocusNow(pane)
        k.newMinibufferWidget = pane
        k.showStateAndMode()
    #@+node:ekr.20150514063305.198: *3* cycleAllFocus (EditCommandsClass)
    editWidgetCount = 0

    def cycleAllFocus(self, event):
        '''
        Cycle the keyboard focus between Leo's outline,
        all body editors and all tabs in the log pane.
        '''
        trace = False and not g.unitTesting
        c, k = self.c, self.c.k
        w = event and event.widget # Does **not** require a text widget.
        pane = None # The widget that will get the new focus.
        log = c.frame.log
        w_name = g.app.gui.widget_name
        if trace: g.trace('**before', w_name(w), 'isLog', log.isLogWidget(w))
        # w may not be the present body widget, so test its name, not its id.
        if w_name(w).find('tree') > -1 or w_name(w).startswith('head'):
            pane = c.frame.body.wrapper
        elif w_name(w).startswith('body'):
            # Cycle through the *body* editor if there are several.
            n = c.frame.body.numberOfEditors
            if n > 1:
                self.editWidgetCount += 1
                if self.editWidgetCount == 1:
                    pane = c.frame.body.wrapper
                elif self.editWidgetCount > n:
                    self.editWidgetCount = 0
                    c.frame.log.selectTab('Log')
                    pane = c.frame.log.logCtrl
                else:
                    c.frame.body.cycleEditorFocus(event)
                    pane = None
            else:
                self.editWidgetCount = 0
                c.frame.log.selectTab('Log')
                pane = c.frame.log.logCtrl
        elif log.isLogWidget(w):
            # A log widget.  Cycle until we come back to 'Log'.
            log.cycleTabFocus()
            pane = c.frame.tree.canvas if log.tabName == 'Log' else None
        else:
            # A safe default: go to the body.
            if trace: g.trace('* default to body')
            pane = c.frame.body.wrapper
        if trace: g.trace('**after', w_name(pane), pane)
        if pane:
            k.newMinibufferWidget = pane
            c.widgetWantsFocusNow(pane)
            k.showStateAndMode()
    #@+node:ekr.20150514063305.199: *3* focusTo...
    @cmd('focus-to-body')
    def focusToBody(self, event=None):
        '''Put the keyboard focus in Leo's body pane.'''
        c, k = self.c, self.c.k
        c.bodyWantsFocus()
        if k:
            k.setDefaultInputState()
            k.showStateAndMode()

    @cmd('focus-to-log')
    def focusToLog(self, event=None):
        '''Put the keyboard focus in Leo's log pane.'''
        self.c.logWantsFocus()

    @cmd('focus-to-minibuffer')
    def focusToMinibuffer(self, event=None):
        '''Put the keyboard focus in Leo's minibuffer.'''
        self.c.minibufferWantsFocus()

    @cmd('focus-to-tree')
    def focusToTree(self, event=None):
        '''Put the keyboard focus in Leo's outline pane.'''
        self.c.treeWantsFocus()
    #@+node:ekr.20150514063305.200: *3* clicks in the headline (leoEditCommands)
    # These call wrappers that trigger hooks.

    @cmd('click-headline')
    def clickHeadline(self, event=None):
        '''Simulate a click in the headline of the presently selected node.'''
        c = self.c
        c.frame.tree.onHeadlineClick(event, c.p)

    @cmd('double-click-headline')
    def doubleClickHeadline(self, event=None):
        '''Simulate a double click in headline of the presently selected node.'''
        c = self.c
        return c.frame.tree.onDoubleClickHeadline(event, c.p)

    @cmd('right-click-headline')
    def rightClickHeadline(self, event=None):
        '''Simulate a right click in the headline of the presently selected node.'''
        c = self.c
        c.frame.tree.onHeadlineRightClick(event, c.p)
    #@+node:ekr.20150514063305.201: *3* clicks in the icon box (leoEditCommands)
    # These call the actual event handlers so as to trigger hooks.

    @cmd('ctrl-click-icon')
    def ctrlClickIconBox(self, event=None):
        '''Simulate a ctrl-click in the icon box of the presently selected node.'''
        c = self.c
        c.frame.tree.OnIconCtrlClick(c.p)
            # Calls the base LeoTree method.

    @cmd('click-icon-box')
    def clickIconBox(self, event=None):
        '''Simulate a click in the icon box of the presently selected node.'''
        c = self.c
        c.frame.tree.onIconBoxClick(event, p=c.p)

    @cmd('double-click-icon-box')
    def doubleClickIconBox(self, event=None):
        '''Simulate a double-click in the icon box of the presently selected node.'''
        c = self.c
        c.frame.tree.onIconBoxDoubleClick(event, p=c.p)

    @cmd('right-click-icon')
    def rightClickIconBox(self, event=None):
        '''Simulate a right click in the icon box of the presently selected node.'''
        c = self.c
        c.frame.tree.onIconBoxRightClick(event, p=c.p)
    #@+node:ekr.20150514063305.202: *3* clickClickBox
    @cmd('click-click-box')
    def clickClickBox(self, event=None):
        '''
        Simulate a click in the click box (+- box) of the presently selected node.

        Call the actual event handlers so as to trigger hooks.
        '''
        c = self.c
        c.frame.tree.onClickBoxClick(event, p=c.p)
    #@+node:ekr.20150514063305.203: *3* simulate...Drag
    # These call the drag setup methods which in turn trigger hooks.

    @cmd('simulate-begin-drag')
    def simulateBeginDrag(self, event=None):
        '''Simulate the start of a drag in the presently selected node.'''
        c = self.c
        c.frame.tree.startDrag(event, p=c.p)

    @cmd('simulate-end-drag')
    def simulateEndDrag(self, event=None):
        '''Simulate the end of a drag in the presently selected node.'''
        c = self.c
        # Note: this assumes that tree.startDrag has already been called.
        c.frame.tree.endDrag(event)
    #@+node:ekr.20150514063305.204: ** color & font
    #@+node:ekr.20150514063305.205: *3* show-colors
    @cmd('show-colors')
    def showColors(self, event):
        '''Open a tab in the log pane showing various color pickers.'''
        c = self.c
        log = c.frame.log
        tabName = 'Colors'
        if log.frameDict.get(tabName):
            log.selectTab(tabName)
        else:
            log.selectTab(tabName)
            log.createColorPicker(tabName)
    #@+node:ekr.20150514063305.206: *3* editCommands.show-fonts & helpers
    @cmd('show-fonts')
    def showFonts(self, event):
        '''Open a tab in the log pane showing a font picker.'''
        c = self.c
        log = c.frame.log
        tabName = 'Fonts'
        if log.frameDict.get(tabName):
            log.selectTab(tabName)
        else:
            log.selectTab(tabName)
            log.createFontPicker(tabName)
    #@+node:ekr.20150514063305.207: ** comment column...
    #@+node:ekr.20150514063305.208: *3* setCommentColumn
    @cmd('set-comment-column')
    def setCommentColumn(self, event):
        '''Set the comment column for the indent-to-comment-column command.'''
        w = self.editWidget(event)
        if w:
            s = w.getAllText()
            ins = w.getInsertPoint()
            row, col = g.convertPythonIndexToRowCol(s, ins)
            self.ccolumn = col
    #@+node:ekr.20150514063305.209: *3* indentToCommentColumn
    @cmd('indent-to-comment-column')
    def indentToCommentColumn(self, event):
        '''
        Insert whitespace to indent the line containing the insert point to the
        comment column.
        '''
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType='indent-to-comment-column')
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        line = s[i: j]
        c1 = int(self.ccolumn)
        line2 = ' ' * c1 + line.lstrip()
        if line2 != line:
            w.delete(i, j)
            w.insert(i, line2)
        w.setInsertPoint(i + c1)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.210: ** esc methods for Python evaluation
    #@+node:ekr.20150514063305.211: *3* watchEscape
    @cmd('escape')
    def watchEscape(self, event):
        '''Enter watch escape mode.'''
        c, k = self.c, self.c.k
        char = event and event.char or ''
        if not k.inState():
            k.setState('escape', 'start', handler=self.watchEscape)
            k.setLabelBlue('Esc ')
        elif k.getStateKind() == 'escape':
            state = k.getState('escape')
            # hi1 = k.keysymHistory [0]
            # hi2 = k.keysymHistory [1]
            data1 = g.app.lossage[0]
            data2 = g.app.lossage[1]
            ch1, stroke1 = data1
            ch2, stroke2 = data2
            if state == 'esc esc' and char == ':':
                self.evalExpression(event)
            elif state == 'evaluate':
                self.escEvaluate(event)
            # elif hi1 == hi2 == 'Escape':
            elif stroke1 == 'Escape' and stroke2 == 'Escape':
                k.setState('escape', 'esc esc')
                k.setLabel('Esc Esc -')
            elif char not in ('Shift_L', 'Shift_R'):
                k.keyboardQuit()
    #@+node:ekr.20150514063305.212: *3* escEvaluate (Revise)
    def escEvaluate(self, event):
        c, k = self.c, self.c.k
        w = self.editWidget(event)
        if not w:
            return
        char = event and event.char or ''
        if k.getLabel() == 'Eval:':
            k.setLabel('')
        if char in ('\n', 'Return'):
            expression = k.getLabel()
            try:
                ok = False
                result = eval(expression, {}, {})
                result = str(result)
                i = w.getInsertPoint()
                w.insert(i, result)
                ok = True
            finally:
                k.keyboardQuit()
                if not ok:
                    k.setStatusLabel('Error: Invalid Expression')
        else:
            k.updateLabel(event)
    #@+node:ekr.20150514063305.213: ** evalExpression
    @cmd('eval-expression')
    def evalExpression(self, event):
        '''Evaluate a Python Expression entered in the minibuffer.'''
        k = self.c.k
        state = k.getState('eval-expression')
        if state == 0:
            k.setLabelBlue('Eval: ')
            k.getArg(event, 'eval-expression', 1, self.evalExpression)
        else:
            k.clearState()
            try:
                e = k.arg
                result = str(eval(e, {}, {}))
                k.setLabelGrey('Eval: %s -> %s' % (e, result))
            except Exception:
                k.setLabelGrey('Invalid Expression: %s' % e)
    #@+node:ekr.20150514063305.214: ** fill column and centering
    #@+at
    # 
    # These methods are currently just used in tandem to center the line or
    # region within the fill column. for example, dependent upon the fill column, this text:
    # 
    # cats
    # raaaaaaaaaaaats
    # mats
    # zaaaaaaaaap
    # 
    # may look like
    # 
    #                                  cats
    #                            raaaaaaaaaaaats
    #                                  mats
    #                              zaaaaaaaaap
    # 
    # after an center-region command via Alt-x.
    #@+node:ekr.20150514063305.215: *3* centerLine
    @cmd('center-line')
    def centerLine(self, event):
        '''Centers line within current fill column'''
        c, k, w = self.c, self.c.k, self.editWidget(event)
        if not w:
            return
        if self.fillColumn > 0:
            fillColumn = self.fillColumn
        else:
            d = c.scanAllDirectives()
            fillColumn = d.get("pagewidth")
        s = w.getAllText()
        i, j = g.getLine(s, w.getInsertPoint())
        line = s[i: j].strip()
        if not line or len(line) >= fillColumn:
            return
        self.beginCommand(w, undoType='center-line')
        n = (fillColumn - len(line)) / 2
        ws = ' ' * n
        k = g.skip_ws(s, i)
        if k > i: w.delete(i, k - i)
        w.insert(i, ws)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.216: *3* setFillColumn
    @cmd('set-fill-column')
    def setFillColumn(self, event):
        '''Set the fill column used by the center-line and center-region commands.'''
        k = self.c.k
        state = k.getState('set-fill-column')
        if state == 0:
            k.setLabelBlue('Set Fill Column: ')
            k.getArg(event, 'set-fill-column', 1, self.setFillColumn)
        else:
            k.clearState()
            try:
                # Bug fix: 2011/05/23: set the fillColumn ivar!
                self.fillColumn = n = int(k.arg)
                k.setLabelGrey('fill column is: %d' % n)
                k.commandName = 'set-fill-column %d' % n
            except ValueError:
                k.resetLabel()
    #@+node:ekr.20150514063305.217: *3* centerRegion
    @cmd('center-region')
    def centerRegion(self, event):
        '''Centers the selected text within the fill column'''
        c, k, w = self.c, self.c.k, self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        sel_1, sel_2 = w.getSelectionRange()
        ind, junk = g.getLine(s, sel_1)
        junk, end = g.getLine(s, sel_2)
        if self.fillColumn > 0:
            fillColumn = self.fillColumn
        else:
            d = c.scanAllDirectives()
            fillColumn = d.get("pagewidth")
        self.beginCommand(w, undoType='center-region')
        inserted = 0
        while ind < end:
            s = w.getAllText()
            i, j = g.getLine(s, ind)
            line = s[i: j].strip()
            # g.trace(len(line),repr(line))
            if len(line) >= fillColumn:
                ind = j
            else:
                n = int((fillColumn - len(line)) / 2)
                inserted += n
                k = g.skip_ws(s, i)
                if k > i: w.delete(i, k - i)
                w.insert(i, ' ' * n)
                ind = j + n - (k - i)
        w.setSelectionRange(sel_1, sel_2 + inserted)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.218: *3* setFillPrefix
    @cmd('set-fill-prefix')
    def setFillPrefix(self, event):
        '''Make the selected text the fill prefix.'''
        w = self.editWidget(event)
        if w:
            s = w.getAllText()
            i, j = w.getSelectionRange()
            self.fillPrefix = s[i: j]
    #@+node:ekr.20150514063305.219: *3* _addPrefix
    def _addPrefix(self, ntxt):
        # pylint: disable=deprecated-lambda
        ntxt = ntxt.split('.')
        ntxt = map(lambda a: self.fillPrefix + a, ntxt)
        ntxt = '.'.join(ntxt)
        return ntxt
    #@+node:ekr.20150514063305.220: ** find (quick)
    #@+node:ekr.20150514063305.221: *3* backward/findCharacter & helper
    @cmd('backward-find-character')
    def backwardFindCharacter(self, event):
        '''Search backwards for a character.'''
        return self.findCharacterHelper(event, backward=True, extend=False)

    @cmd('backward-find-character-extend-selection')
    def backwardFindCharacterExtendSelection(self, event):
        '''Search backward for a character, extending the selection.'''
        return self.findCharacterHelper(event, backward=True, extend=True)

    @cmd('find-character')
    def findCharacter(self, event):
        '''Search for a character.'''
        return self.findCharacterHelper(event, backward=False, extend=False)

    @cmd('find-character-extend-selection')
    def findCharacterExtendSelection(self, event):
        '''Search for a character, extending the selection.'''
        return self.findCharacterHelper(event, backward=False, extend=True)
    #@+node:ekr.20150514063305.222: *4* findCharacterHelper
    def findCharacterHelper(self, event, backward, extend):
        '''Put the cursor at the next occurance of a character on a line.'''
        c, k = self.c, self.c.k
        tag = 'find-char'
        state = k.getState(tag)
        if state == 0:
            self.w = self.editWidget(event)
            if not self.w:
                return
            self.event = event
            self.backward = backward
            self.extend = extend or self.extendMode # Bug fix: 2010/01/19
            self.insert = self.w.getInsertPoint()
            s = '%s character%s: ' % (
                'Backward find' if backward else 'Find',
                ' & extend' if extend else '')
            k.setLabelBlue(s)
            # Get the arg without touching the focus.
            k.getArg(event, tag, 1, self.findCharacter, oneCharacter=True, useMinibuffer=False)
        else:
            event, w = self.event, self.w
            backward = self.backward
            extend = self.extend or self.extendMode
            ch = k.arg
            s = w.getAllText()
            ins = w.toPythonIndex(self.insert)
            i = ins + -1 if backward else + 1 # skip the present character.
            if backward:
                start = 0
                j = s.rfind(ch, start, max(start, i)) # Skip the character at the cursor.
                if j > -1: self.moveToHelper(event, j, extend)
            else:
                end = len(s)
                j = s.find(ch, min(i, end), end) # Skip the character at the cursor.
                if j > -1: self.moveToHelper(event, j, extend)
            k.resetLabel()
            k.clearState()
    #@+node:ekr.20150514063305.223: *3* findWord and FindWordOnLine & helper
    @cmd('find-word')
    def findWord(self, event):
        '''Put the cursor at the next word that starts with a character.'''
        return self.findWordHelper(event, oneLine=False)

    @cmd('find-word-in-line')
    def findWordInLine(self, event):
        '''Put the cursor at the next word (on a line) that starts with a character.'''
        return self.findWordHelper(event, oneLine=True)
    #@+node:ekr.20150514063305.224: *4* findWordHelper
    def findWordHelper(self, event, oneLine):
        k = self.c.k
        tag = 'find-word'
        state = k.getState(tag)
        if state == 0:
            self.w = self.editWidget(event)
            if not self.w:
                return
            self.oneLineFlag = oneLine
            k.setLabelBlue('Find word %sstarting with: ' % (
                'in line ' if oneLine else ''))
            k.getArg(event, tag, 1, self.findWord, oneCharacter=True)
        else:
            ch = k.arg
            if ch:
                w = self.w
                i = w.getInsertPoint()
                s = w.getAllText()
                end = len(s)
                if self.oneLineFlag:
                    end = s.find('\n', i) # Limit searches to this line.
                    if end == -1: end = len(s)
                while i < end:
                    i = s.find(ch, i + 1, end) # Ensure progress and i > 0.
                    if i == -1:
                        break
                    elif not g.isWordChar(s[i - 1]):
                        w.setSelectionRange(i, i, insert=i)
                        break
            k.resetLabel()
            k.clearState()
    #@+node:ekr.20150514063305.225: ** goto...
    #@+node:ekr.20150514063305.226: *3* gotoCharacter
    @cmd('goto-char')
    def gotoCharacter(self, event):
        '''Put the cursor at the n'th character of the buffer.'''
        k = self.c.k
        state = k.getState('goto-char')
        if state == 0:
            self.w = self.editWidget(event)
            if self.w:
                k.setLabelBlue("Goto n'th character: ")
                k.getArg(event, 'goto-char', 1, self.gotoCharacter)
        else:
            n = k.arg
            w = self.w
            ok = False
            if n.isdigit():
                n = int(n)
                if n >= 0:
                    w.setInsertPoint(n)
                    w.seeInsertPoint()
                    ok = True
            if not ok:
                g.warning('goto-char takes non-negative integer argument')
            k.resetLabel()
            k.clearState()
    #@+node:ekr.20150514063305.227: *3* gotoGlobalLine (leoEditCommands)
    @cmd('goto-global-line')
    def gotoGlobalLine(self, event):
        '''
        Put the cursor at the n'th line of a file or script. This is a
        minibuffer interface to Leo's legacy Go To Line number command.
        '''
        c, k = self.c, self.c.k
        tag = 'goto-global-line'
        state = k.getState(tag)
        if state == 0:
            self.w = self.editWidget(event)
            if self.w:
                k.setLabelBlue('Goto global line: ')
                k.getArg(event, tag, 1, self.gotoGlobalLine)
        else:
            n = k.arg
            k.resetLabel()
            k.clearState()
            if n.isdigit():
                c.gotoCommands.find_file_line(n=int(n))
    #@+node:ekr.20150514063305.228: *3* gotoLine
    @cmd('goto-line')
    def gotoLine(self, event):
        '''Put the cursor at the n'th line of the buffer.'''
        k = self.c.k
        state = k.getState('goto-line')
        if state == 0:
            self.w = self.editWidget(event)
            if self.w:
                k.setLabelBlue('Goto line: ')
                k.getArg(event, 'goto-line', 1, self.gotoLine)
        else:
            n, w = k.arg, self.w
            if n.isdigit():
                s = w.getAllText()
                i = g.convertRowColToPythonIndex(s, n, 0)
                w.setInsertPoint(i)
                w.seeInsertPoint()
            k.resetLabel()
            k.clearState()
    #@+node:ekr.20150514063305.229: ** icons... (leoEditCommands)
    #@+at
    # 
    # To do:
    # 
    # - Define standard icons in a subfolder of Icons folder?
    # - Tree control recomputes height of each line.
    #@+node:ekr.20150514063305.230: *3*  Helpers
    #@+node:ekr.20150514063305.231: *4* appendImageDictToList
    def appendImageDictToList(self, aList, iconDir, path, xoffset, **kargs):
        c = self.c
        path = c.os_path_finalize_join(iconDir, path)
        relPath = g.makePathRelativeTo(path, iconDir)
        # pylint: disable=unpacking-non-sequence
        image, image_height = g.app.gui.getTreeImage(c, path)
        if not image:
            g.es('can not load image:', path)
            return xoffset
        if image_height is None:
            yoffset = 0
        else:
            yoffset = 0 # (c.frame.tree.line_height-image_height)/2
            # TNB: I suspect this is being done again in the drawing code
        newEntry = {
            'type': 'file',
            'file': path,
            'relPath': relPath,
            'where': 'beforeHeadline',
            'yoffset': yoffset, 'xoffset': xoffset, 'xpad': 1, # -2,
            'on': 'VNode',
        }
        newEntry.update(kargs) # may switch 'on' to 'VNode'
        aList.append(newEntry)
        xoffset += 2
        return xoffset
    #@+node:ekr.20150514063305.232: *4* dHash
    def dHash(self, d):
        """Hash a dictionary"""
        return ''.join(['%s%s' % (str(k), str(d[k])) for k in sorted(d)])
    #@+node:ekr.20150514063305.233: *4* getIconList
    def getIconList(self, p):
        """Return list of icons for position p, call setIconList to apply changes"""
        trace = False and not g.unitTesting
        if trace:
            if p == self.c.rootPosition(): g.trace('=' * 40)
            g.trace(p.h)
        fromVnode = []
        if hasattr(p.v, 'unknownAttributes'):
            if trace: g.trace(p.v.u)
            fromVnode = [dict(i) for i in p.v.u.get('icons', [])]
            for i in fromVnode: i['on'] = 'VNode'
        if trace and fromVnode: g.trace('fromVnode', fromVnode, p.h)
        return fromVnode
    #@+node:ekr.20150514063305.234: *4* setIconList & helpers
    def setIconList(self, p, l, setDirty=True):
        """Set list of icons for position p to l"""
        trace = False and not g.unitTesting
        current = self.getIconList(p)
        if not l and not current: return # nothing to do
        lHash = ''.join([self.dHash(i) for i in l])
        cHash = ''.join([self.dHash(i) for i in current])
        # if trace: g.trace('lHash:',lHash)
        # if trace: g.trace('cHash:',cHash)
        if lHash == cHash:
            # no difference between original and current list of dictionaries
            return
        if trace: g.trace(l, g.callers(6))
        self._setIconListHelper(p, l, p.v, setDirty)
    #@+node:ekr.20150514063305.235: *5* _setIconListHelper
    def _setIconListHelper(self, p, subl, uaLoc, setDirty):
        """icon setting code common between v and t nodes

        p - postion
        subl - list of icons for the v or t node
        uaLoc - the v or t node
        """
        trace = False and not g.unitTesting
        if subl: # Update the uA.
            if not hasattr(uaLoc, 'unknownAttributes'):
                uaLoc.unknownAttributes = {}
            uaLoc.unknownAttributes['icons'] = list(subl)
            # g.es((p.h,uaLoc.unknownAttributes['icons']))
            uaLoc._p_changed = 1
            if setDirty:
                p.setDirty()
            if trace: g.trace('uA', uaLoc.u, uaLoc)
        else: # delete the uA.
            if hasattr(uaLoc, 'unknownAttributes'):
                if 'icons' in uaLoc.unknownAttributes:
                    del uaLoc.unknownAttributes['icons']
                    uaLoc._p_changed = 1
                    if setDirty:
                        p.setDirty()
            if trace: g.trace('del uA[icons]', uaLoc)
    #@+node:ekr.20150514063305.236: *3* deleteFirstIcon
    @cmd('delete-first-icon')
    def deleteFirstIcon(self, event=None):
        '''Delete the first icon in the selected node's icon list.'''
        c = self.c
        aList = self.getIconList(c.p)
        if aList:
            self.setIconList(c.p, aList[1:])
            c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20150514063305.237: *3* deleteIconByName
    def deleteIconByName(self, t, name, relPath): # t not used.
        """for use by the right-click remove icon callback"""
        c, p = self.c, self.c.p
        aList = self.getIconList(p)
        if not aList:
            return
        basePath = c.os_path_finalize_join(g.app.loadDir, "..", "Icons")
        absRelPath = c.os_path_finalize_join(basePath, relPath)
        name = c.os_path_finalize(name)
        newList = []
        for d in aList:
            name2 = d.get('file')
            name2 = c.os_path_finalize(name2)
            name2rel = d.get('relPath')
            # g.trace('name',name,'\nrelPath',relPath,'\nabsRelPath',absRelPath,'\nname2',name2,'\nname2rel',name2rel)
            if not (name == name2 or absRelPath == name2 or relPath == name2rel):
                newList.append(d)
        if len(newList) != len(aList):
            self.setIconList(p, newList)
            c.setChanged(True)
            c.redraw_after_icons_changed()
        else:
            g.trace('not found', name)
    #@+node:ekr.20150514063305.238: *3* deleteLastIcon
    @cmd('delete-last-icon')
    def deleteLastIcon(self, event=None):
        '''Delete the first icon in the selected node's icon list.'''
        c = self.c
        aList = self.getIconList(c.p)
        if aList:
            self.setIconList(c.p, aList[: -1])
            c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20150514063305.239: *3* deleteNodeIcons
    @cmd('delete-node-icons')
    def deleteNodeIcons(self, event=None, p=None):
        '''Delete all of the selected node's icons.'''
        c = self.c
        p = p or c.p
        if p.u:
            a = p.v.unknownAttributes
            p.v._p_changed = 1
            self.setIconList(p, [])
            p.setDirty()
            c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20150514063305.240: *3* insertIcon
    @cmd('insert-icon')
    def insertIcon(self, event=None):
        '''Prompt for an icon, and insert it into the node's icon list.'''
        c, p = self.c, self.c.p
        iconDir = c.os_path_finalize_join(g.app.loadDir, "..", "Icons")
        os.chdir(iconDir)
        paths = g.app.gui.runOpenFileDialog(c,
            title='Get Icons',
            filetypes=[('All files', '*'), ('Gif', '*.gif'), ('Bitmap', '*.bmp'), ('Icon', '*.ico'),],
            defaultextension=None,
            multiple=True)
        if not paths: return
        aList = []
        xoffset = 2
        for path in paths:
            xoffset = self.appendImageDictToList(aList, iconDir, path, xoffset)
        aList2 = self.getIconList(p)
        aList2.extend(aList)
        self.setIconList(p, aList2)
        c.setChanged(True)
        c.redraw_after_icons_changed()
    #@+node:ekr.20150514063305.241: *3* insertIconFromFile
    def insertIconFromFile(self, path, p=None, pos=None, **kargs):
        c = self.c
        if not p: p = c.p
        iconDir = c.os_path_finalize_join(g.app.loadDir, "..", "Icons")
        os.chdir(iconDir)
        aList = []
        xoffset = 2
        xoffset = self.appendImageDictToList(aList, iconDir, path, xoffset, **kargs)
        aList2 = self.getIconList(p)
        if pos is None: pos = len(aList2)
        aList2.insert(pos, aList[0])
        self.setIconList(p, aList2)
        c.setChanged(True)
        c.redraw_after_icons_changed()
    #@+node:ekr.20150514063305.242: ** indent...
    #@+node:ekr.20150514063305.243: *3* deleteIndentation
    @cmd('delete-indentation')
    def deleteIndentation(self, event):
        '''Delete indentation in the presently line.'''
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        line = s[i: j]
        line2 = s[i: j].lstrip()
        delta = len(line) - len(line2)
        if delta:
            self.beginCommand(w, undoType='delete-indentation')
            w.delete(i, j)
            w.insert(i, line2)
            ins -= delta
            w.setSelectionRange(ins, ins, insert=ins)
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.244: *3* indentRelative
    @cmd('indent-relative')
    def indentRelative(self, event):
        '''
        The indent-relative command indents at the point based on the previous
        line (actually, the last non-empty line.) It inserts whitespace at the
        point, moving point, until it is underneath an indentation point in the
        previous line.

        An indentation point is the end of a sequence of whitespace or the end of
        the line. If the point is farther right than any indentation point in the
        previous line, the whitespace before point is deleted and the first
        indentation point then applicable is used. If no indentation point is
        applicable even then whitespace equivalent to a single tab is inserted.
        '''
        c = self.c
        undoType = 'indent-relative'
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        oldSel = w.getSelectionRange()
        oldYview = w.getYScrollPosition()
        # Find the previous non-blank line
        i, j = g.getLine(s, ins)
        while 1:
            if i <= 0: return
            i, j = g.getLine(s, i - 1)
            line = s[i: j]
            if line.strip(): break
        self.beginCommand(w, undoType=undoType)
        try:
            k = g.skip_ws(s, i)
            ws = s[i: k]
            i2, j2 = g.getLine(s, ins)
            k = g.skip_ws(s, i2)
            line = ws + s[k: j2]
            w.delete(i2, j2)
            w.insert(i2, line)
            w.setInsertPoint(i2 + len(ws))
            c.frame.body.onBodyChanged(undoType, oldSel=oldSel, oldText=s, oldYview=oldYview)
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.245: ** info...
    #@+node:ekr.20150514063305.246: *3* howMany
    @cmd('how-many')
    def howMany(self, event):
        '''
        Print how many occurances of a regular expression are found
        in the body text of the presently selected node.
        '''
        k = self.c.k
        w = self.editWidget(event)
        if not w:
            return
        state = k.getState('how-many')
        if state == 0:
            k.setLabelBlue('How many: ')
            k.getArg(event, 'how-many', 1, self.howMany)
        else:
            k.clearState()
            s = w.getAllText()
            reg = re.compile(k.arg)
            i = reg.findall(s)
            k.setLabelGrey('%s occurances of %s' % (len(i), k.arg))
    #@+node:ekr.20150514063305.247: *3* lineNumber
    @cmd('line-number')
    def lineNumber(self, event):
        '''Print the line and column number and percentage of insert point.'''
        k = self.c.k
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        i = w.getInsertPoint()
        row, col = g.convertPythonIndexToRowCol(s, i)
        percent = int((i * 100) / len(s))
        k.setLabelGrey(
            'char: %s row: %d col: %d pos: %d (%d%% of %d)' % (
                repr(s[i]), row, col, i, percent, len(s)))
    #@+node:ekr.20150514063305.248: *3* k.viewLossage
    @cmd('view-lossage')
    def viewLossage(self, event):
        '''Put the Emacs-lossage in the minibuffer label.'''
        k = self.c.k
        g.es('lossage...')
        aList = g.app.lossage
        aList.reverse()
        for data in aList:
            ch, stroke = data
            g.es('', k.prettyPrintKey(stroke))
    #@+node:ekr.20150514063305.249: *3* whatLine
    @cmd('what-line')
    def whatLine(self, event):
        '''Print the line number of the line containing the cursor.'''
        k = self.c.k
        w = self.editWidget(event)
        if w:
            s = w.getAllText()
            i = w.getInsertPoint()
            row, col = g.convertPythonIndexToRowCol(s, i)
            k.keyboardQuit()
            k.setStatusLabel("Line %s" % row)
    #@+node:ekr.20150514063305.250: ** insert & delete...
    #@+node:ekr.20150514063305.251: *3* addSpace/TabToLines & removeSpace/TabFromLines & helper
    @cmd('add-space-to-lines')
    def addSpaceToLines(self, event):
        '''Add a space to start of all lines, or all selected lines.'''
        self.addRemoveHelper(event, ch=' ', add=True, undoType='add-space-to-lines')

    @cmd('add-tab-to-lines')
    def addTabToLines(self, event):
        '''Add a tab to start of all lines, or all selected lines.'''
        self.addRemoveHelper(event, ch='\t', add=True, undoType='add-tab-to-lines')

    @cmd('remove-space-from-lines')
    def removeSpaceFromLines(self, event):
        '''Remove a space from start of all lines, or all selected lines.'''
        self.addRemoveHelper(event, ch=' ', add=False, undoType='remove-space-from-lines')

    @cmd('remove-tab-from-lines')
    def removeTabFromLines(self, event):
        '''Remove a tab from start of all lines, or all selected lines.'''
        self.addRemoveHelper(event, ch='\t', add=False, undoType='remove-tab-from-lines')
    #@+node:ekr.20150514063305.252: *4* addRemoveHelper
    def addRemoveHelper(self, event, ch, add, undoType):
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        if w.hasSelection(): s = w.getSelectedText()
        else: s = w.getAllText()
        if not s:
            return
        # Insert or delete spaces instead of tabs when negative tab width is in effect.
        d = c.scanAllDirectives()
        width = d.get('tabwidth')
        if ch == '\t' and width < 0: ch = ' ' * abs(width)
        self.beginCommand(w, undoType=undoType)
        lines = g.splitLines(s)
        if add:
            result = [ch + line for line in lines]
        else:
            result = [line[len(ch):] if line.startswith(ch) else line for line in lines]
        result = ''.join(result)
        # g.trace('add',add,'hasSelection',w.hasSelection(),'result',repr(result))
        if w.hasSelection():
            i, j = w.getSelectionRange()
            w.delete(i, j)
            w.insert(i, result)
            w.setSelectionRange(i, i + len(result))
        else:
            w.setAllText(result)
            w.setSelectionRange(0, len(s))
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.253: *3* backwardDeleteCharacter
    @cmd('backward-delete-char')
    def backwardDeleteCharacter(self, event=None):
        '''Delete the character to the left of the cursor.'''
        c, p = self.c, self.c.p
        w = self.editWidget(event)
        if not w:
            return
        wname = c.widget_name(w)
        ins = w.getInsertPoint()
        i, j = w.getSelectionRange()
        if wname.startswith('body'):
            self.beginCommand(w)
            try:
                tab_width = c.getTabWidth(c.p)
                changed = True
                if i != j:
                    w.delete(i, j)
                    w.setSelectionRange(i, i, insert=i)
                elif i == 0:
                    changed = False
                elif tab_width > 0:
                    w.delete(ins - 1)
                    w.setSelectionRange(ins - 1, ins - 1, insert=ins - 1)
                else:
                    #@+<< backspace with negative tab_width >>
                    #@+node:ekr.20150514063305.254: *4* << backspace with negative tab_width >>
                    s = prev = w.getAllText()
                    ins = w.getInsertPoint()
                    i, j = g.getLine(s, ins)
                    s = prev = s[i: ins]
                    n = len(prev)
                    abs_width = abs(tab_width)
                    # Delete up to this many spaces.
                    n2 = (n % abs_width) or abs_width
                    n2 = min(n, n2)
                    count = 0
                    while n2 > 0:
                        n2 -= 1
                        ch = prev[n - count - 1]
                        if ch != ' ': break
                        else: count += 1
                    # Make sure we actually delete something.
                    i = ins - (max(1, count))
                    w.delete(i, ins)
                    w.setSelectionRange(i, i, insert=i)
                    #@-<< backspace with negative tab_width >>
            finally:
                self.endCommand(changed=changed, setLabel=False)
                    # Necessary to make text changes stick.
        else:
            # No undo in this widget.
            # Make sure we actually delete something if we can.
            s = w.getAllText()
            if i != j:
                j = max(i, min(j, len(s)))
                w.delete(i, j)
                w.setSelectionRange(i, i, insert=i)
            elif ins != 0:
                # Do nothing at the start of the headline.
                w.delete(ins - 1)
                ins = ins - 1
                w.setSelectionRange(ins, ins, insert=ins)
    #@+node:ekr.20150514063305.255: *3* cleanAllLines
    @cmd('clean-all-lines')
    def cleanAllLines(self, event):
        '''Clean all lines in the selected tree.'''
        c = self.c
        u = c.undoer
        w = c.frame.body.wrapper
        if not w: return
        tag = 'clean-all-lines'
        u.beforeChangeGroup(c.p, tag)
        n = 0
        for p in c.p.self_and_subtree():
            lines = []
            for line in g.splitLines(p.b):
                if line.rstrip():
                    lines.append(line.rstrip())
                if line.endswith('\n'):
                    lines.append('\n')
            s2 = ''.join(lines)
            if s2 != p.b:
                print(p.h)
                bunch = u.beforeChangeNodeContents(p)
                p.b = s2
                p.v.setDirty()
                n += 1
                u.afterChangeNodeContents(p, tag, bunch)
        u.afterChangeGroup(c.p, tag)
        c.redraw_after_icons_changed()
        g.es('cleaned %s nodes' % n)
    #@+node:ekr.20150514063305.256: *3* cleanLines
    @cmd('clean-lines')
    def cleanLines(self, event):
        '''Removes trailing whitespace from all lines, preserving newlines.
        '''
        w = self.editWidget(event)
        if not w:
            return
        if w.hasSelection():
            s = w.getSelectedText()
        else:
            s = w.getAllText()
        lines = []
        for line in g.splitlines(s):
            if line.rstrip():
                lines.append(line.rstrip())
            if line.endswith('\n'):
                lines.append('\n')
        result = ''.join(lines)
        if s != result:
            self.beginCommand(w, undoType='clean-lines')
            if w.hasSelection():
                i, j = w.getSelectionRange()
                w.delete(i, j)
                w.insert(i, result)
                w.setSelectionRange(i, j + len(result))
            else:
                i = w.getInsertPoint()
                w.delete(0, 'end')
                w.insert(0, result)
                w.setInsertPoint(i)
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.257: *3* clearSelectedText
    @cmd('clear-selected-text')
    def clearSelectedText(self, event):
        '''Delete the selected text.'''
        w = self.editWidget(event)
        if not w: return
        i, j = w.getSelectionRange()
        if i == j: return
        self.beginCommand(w, undoType='clear-selected-text')
        w.delete(i, j)
        w.setInsertPoint(i)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.258: *3* delete-word & backward-delete-word
    @cmd('delete-word')
    def deleteWord(self, event=None):
        '''Delete the word at the cursor.'''
        self.deleteWordHelper(event, forward=True)

    @cmd('backward-delete-word')
    def backwardDeleteWord(self, event=None):
        '''Delete the word in front of the cursor.'''
        self.deleteWordHelper(event, forward=False)
    # Patch by NH2.

    @cmd('delete-word-smart')
    def deleteWordSmart(self, event=None):
        '''Delete the word at the cursor, treating whitespace
        and symbols smartly.'''
        self.deleteWordHelper(event, forward=True, smart=True)

    @cmd('backward-delete-word-smart')
    def backwardDeleteWordSmart(self, event=None):
        '''Delete the word in front of the cursor, treating whitespace
        and symbols smartly.'''
        self.deleteWordHelper(event, forward=False, smart=True)

    def deleteWordHelper(self, event, forward, smart=False):
        c, w = self.c, self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType="delete-word")
        if w.hasSelection():
            from_pos, to_pos = w.getSelectionRange()
        else:
            from_pos = w.getInsertPoint()
            self.moveWordHelper(event, extend=False, forward=forward, smart=smart)
            to_pos = w.getInsertPoint()
        # For Tk GUI, make sure to_pos > from_pos
        if from_pos > to_pos:
            from_pos, to_pos = to_pos, from_pos
        w.delete(from_pos, to_pos)
        c.frame.body.forceFullRecolor()
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.259: *3* deleteNextChar
    @cmd('delete-char')
    def deleteNextChar(self, event):
        '''Delete the character to the right of the cursor.'''
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        i, j = w.getSelectionRange()
        self.beginCommand(w, undoType='delete-char')
        changed = True
        if i != j:
            w.delete(i, j)
            w.setInsertPoint(i)
        elif j < len(s):
            w.delete(i)
            w.setInsertPoint(i)
        else:
            changed = False
        self.endCommand(changed=changed, setLabel=False)
    #@+node:ekr.20150514063305.260: *3* deleteSpaces
    @cmd('delete-spaces')
    def deleteSpaces(self, event, insertspace=False):
        '''Delete all whitespace surrounding the cursor.'''
        w = self.editWidget(event)
        if not w:
            return
        undoType = 'insert-space' if insertspace else 'delete-spaces'
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        w1 = ins - 1
        while w1 >= i and s[w1].isspace():
            w1 -= 1
        w1 += 1
        w2 = ins
        while w2 <= j and s[w2].isspace():
            w2 += 1
        spaces = s[w1: w2]
        if spaces:
            self.beginCommand(w, undoType=undoType)
            if insertspace: s = s[: w1] + ' ' + s[w2:]
            else: s = s[: w1] + s[w2:]
            w.setAllText(s)
            w.setInsertPoint(w1)
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.261: *3* insertHardTab
    @cmd('insert-hard-tab')
    def insertHardTab(self, event):
        '''Insert one hard tab.'''
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        assert g.isTextWrapper(w)
        name = c.widget_name(w)
        if name.startswith('head'):
            return
        ins = w.getInsertPoint()
        self.beginCommand(w, undoType='insert-hard-tab')
        w.insert(ins, '\t')
        ins += 1
        w.setSelectionRange(ins, ins, insert=ins)
        self.endCommand()
    #@+node:ekr.20150514063305.262: *3* insertNewLine
    @cmd('insert-newline')
    def insertNewLine(self, event):
        '''Insert a newline at the cursor.'''
        c, k = self.c, self.c.k
        w = self.editWidget(event)
        if not w:
            return
        assert g.isTextWrapper(w)
        name = c.widget_name(w)
        if name.startswith('head'):
            return
        oldSel = w.getSelectionRange()
        self.beginCommand(w, undoType='newline')
        self.insertNewlineHelper(w=w, oldSel=oldSel, undoType=None)
        k.setInputState('insert')
        k.showStateAndMode()
        self.endCommand()

    insertNewline = insertNewLine
    #@+node:ekr.20150514063305.263: *3* insertNewLineAndTab
    @cmd('newline-and-indent')
    def insertNewLineAndTab(self, event):
        '''Insert a newline and tab at the cursor.'''
        c, k = self.c, self.c.k
        p = c.p
        w = self.editWidget(event)
        if not w:
            return
        assert g.isTextWrapper(w), w
        name = c.widget_name(w)
        if name.startswith('head'):
            return
        self.beginCommand(w, undoType='insert-newline-and-indent')
        oldSel = w.getSelectionRange()
        self.insertNewlineHelper(w=w, oldSel=oldSel, undoType=None)
        self.updateTab(p, w, smartTab=False)
        k.setInputState('insert')
        k.showStateAndMode()
        self.endCommand(changed=True, setLabel=False)
    #@+node:ekr.20150514063305.264: *3* insertParentheses
    @cmd('insert-parentheses')
    def insertParentheses(self, event):
        '''Insert () at the cursor.'''
        w = self.editWidget(event)
        if w:
            self.beginCommand(w, undoType='insert-parenthesis')
            i = w.getInsertPoint()
            w.insert(i, '()')
            w.setInsertPoint(i + 1)
            self.endCommand(changed=True, setLabel=False)
    #@+node:ekr.20150514063305.265: *3* insertSoftTab
    @cmd('insert-soft-tab')
    def insertSoftTab(self, event):
        '''Insert spaces equivalent to one tab.'''
        c, p = self.c, self.c.p
        w = self.editWidget(event)
        if not w:
            return
        assert g.isTextWrapper(w)
        name = c.widget_name(w)
        if name.startswith('head'): return
        tab_width = abs(c.getTabWidth(c.p))
        ins = w.getInsertPoint()
        self.beginCommand(w, undoType='insert-soft-tab')
        w.insert(ins, ' ' * tab_width)
        ins += tab_width
        w.setSelectionRange(ins, ins, insert=ins)
        self.endCommand()
    #@+node:ekr.20150514063305.266: *3* removeBlankLines
    @cmd('remove-blank-lines')
    def removeBlankLines(self, event):
        '''
        Remove lines containing nothing but whitespace.

        Select all lines if there is no existing selection.
        '''
        c = self.c
        w = self.editWidget(event)
        expandSelection = not w.hasSelection()
        head, lines, tail, oldSel, oldYview = c.getBodyLines(expandSelection=expandSelection)
        changed, result = False, []
        for line in lines:
            if line.strip():
                result.append(line)
            else:
                changed = True
        result = ''.join(result)
        if changed:
            oldSel, undoType = None, 'remove-blank-lines'
            c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview)
    #@+node:ekr.20150514063305.267: *3* replaceCurrentCharacter
    @cmd('replace-current-character')
    def replaceCurrentCharacter(self, event):
        '''Replace the current character with the next character typed.'''
        k = self.c.k
        tag = 'replace-current-character'
        state = k.getState(tag)
        if state == 0:
            self.w = self.editWidget(event)
            if self.w:
                k.setLabelBlue('Replace Character: ')
                k.getArg(event, tag, 1, self.replaceCurrentCharacter)
        else:
            w = self.w
            ch = k.arg
            if ch:
                i, j = w.getSelectionRange()
                if i > j: i, j = j, i
                # Use raw insert/delete to retain the coloring.
                if i == j:
                    i = max(0, i - 1)
                    w.delete(i)
                else:
                    w.delete(i, j)
                w.insert(i, ch)
                w.setInsertPoint(i + 1)
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
    #@+node:ekr.20150514063305.268: *3* selfInsertCommand, helpers
    @cmd('self-insert-command')
    def selfInsertCommand(self, event, action='insert'):
        '''
        Insert a character in the body pane.

        This is the default binding for all keys in the body pane.
        It handles undo, bodykey events, tabs, back-spaces and bracket matching.
        '''
        trace = False and not g.unitTesting
        c, k, p = self.c, self.c.k, self.c.p
        verbose = True
        w = self.editWidget(event)
        if not w:
            return
        #@+<< set local vars >>
        #@+node:ekr.20150514063305.269: *4* << set local vars >> (selfInsertCommand)
        stroke = event and event.stroke or None
        ch = event and event.char or ''
        if ch == 'Return':
            ch = '\n' # This fixes the MacOS return bug.
        if ch == 'Tab':
            ch = '\t'
        name = c.widget_name(w)
        oldSel = name.startswith('body') and w.getSelectionRange() or (None, None)
        oldText = name.startswith('body') and p.b or ''
        undoType = 'Typing'
        brackets = self.openBracketsList + self.closeBracketsList
        inBrackets = ch and g.toUnicode(ch) in brackets
        #@-<< set local vars >>
        assert g.isStrokeOrNone(stroke)
        if trace: g.trace('ch', repr(ch), 'stroke', stroke)
        if g.doHook("bodykey1", c=c, p=p, v=p, ch=ch, oldSel=oldSel, undoType=undoType):
            return
        if ch == '\t':
            self.updateTab(p, w)
        elif ch == '\b':
            # This is correct: we only come here if there no bindngs for this key.
            self.backwardDeleteCharacter(event)
        elif ch in ('\r', '\n'):
            ch = '\n'
            self.insertNewlineHelper(w, oldSel, undoType)
        elif inBrackets and self.autocompleteBrackets:
            self.updateAutomatchBracket(p, w, ch, oldSel)
        elif ch: # Null chars must not delete the selection.
            isPlain = stroke.find('Alt') == -1 and stroke.find('Ctrl') == -1
            i, j = oldSel
            if i > j: i, j = j, i
            # Use raw insert/delete to retain the coloring.
            if i != j: w.delete(i, j)
            elif action == 'overwrite': w.delete(i)
            if isPlain:
                w.insert(i, ch)
                w.setInsertPoint(i + 1)
            else:
                g.app.gui.insertKeyEvent(event, i)
            if inBrackets and self.flashMatchingBrackets:
                self.flashMatchingBracketsHelper(c, ch, i, p, w)
        else:
            return
        # Set the column for up and down keys.
        spot = w.getInsertPoint()
        c.editCommands.setMoveCol(w, spot)
        # Update the text and handle undo.
        newText = w.getAllText()
        changed = newText != oldText
        if trace and verbose:
            g.trace('ch', repr(ch), 'changed', changed, 'newText', repr(newText[-10:]))
        if changed:
            c.frame.body.onBodyChanged(undoType=undoType,
                oldSel=oldSel, oldText=oldText, oldYview=None)
        g.doHook("bodykey2", c=c, p=p, v=p, ch=ch, oldSel=oldSel, undoType=undoType)
    #@+node:ekr.20150514063305.270: *4* doPlainTab
    def doPlainTab(self, s, i, tab_width, w):
        '''Insert spaces equivalent to one tab.'''
        start, end = g.getLine(s, i)
        s2 = s[start: i]
        width = g.computeWidth(s2, tab_width)
        if tab_width > 0:
            w.insert(i, '\t')
            ins = i + 1
        else:
            n = abs(tab_width) - (width % abs(tab_width))
            w.insert(i, ' ' * n)
            ins = i + n
        w.setSelectionRange(ins, ins, insert=ins)
    #@+node:ekr.20150514063305.271: *4* flashCharacter (leoEditCommands)
    def flashCharacter(self, w, i):
        '''Flash the character at position i of widget w.'''
        bg = self.bracketsFlashBg or 'DodgerBlue1'
        fg = self.bracketsFlashFg or 'white'
        flashes = self.bracketsFlashCount or 3
        delay = self.bracketsFlashDelay or 75
        w.flashCharacter(i, bg, fg, flashes, delay)
    #@+node:ekr.20150514063305.272: *4* flashMatchingBracketsHelper (leoEditCommands)
    def flashMatchingBracketsHelper(self, c, ch, i, p, w):
        '''Flash matching brackets at char ch at position i at widget w.'''
        d = {}
        if ch in self.openBracketsList:
            for z in range(len(self.openBracketsList)):
                d[self.openBracketsList[z]] = self.closeBracketsList[z]
            reverse = False # Search forward
        else:
            for z in range(len(self.openBracketsList)):
                d[self.closeBracketsList[z]] = self.openBracketsList[z]
            reverse = True # Search backward
        delim2 = d.get(ch)
        s = w.getAllText()
        # A partial fix for bug 127: Bracket matching is buggy.
        language = g.getLanguageAtPosition(c, p)
        if language ==  'perl':
            return
        j = g.MatchBrackets(c, p, language).find_matching_bracket(ch, s, i)
        if j is not None:
            self.flashCharacter(w, j)

    #@+node:ekr.20150514063305.273: *4* initBracketMatcher
    def initBracketMatcher(self, c):
        '''Init the bracket matching code in selfInsertCommand.'''
        if len(self.openBracketsList) != len(self.closeBracketsList):
            g.es_print('bad open/close_flash_brackets setting: using defaults')
            self.openBracketsList = '([{'
            self.closeBracketsList = ')]}'
        # g.trace('self.openBrackets',openBrackets)
        # g.trace('self.closeBrackets',closeBrackets)
    #@+node:ekr.20150514063305.274: *4* insertNewlineHelper
    def insertNewlineHelper(self, w, oldSel, undoType):
        trace = False and not g.unitTesting
        c, p = self.c, self.c.p
        i, j = oldSel
        ch = '\n'
        if trace:
            s = w.widget.toPlainText()
            g.trace(i, j, len(s), w)
        if i != j:
            # No auto-indent if there is selected text.
            w.delete(i, j)
            w.insert(i, ch)
            w.setInsertPoint(i + 1)
        else:
            w.insert(i, ch)
            w.setInsertPoint(i + 1)
            if (c.autoindent_in_nocolor or
                (c.frame.body.colorizer.useSyntaxColoring(p) and
                undoType != "Change")
            ):
                # No auto-indent if in @nocolor mode or after a Change command.
                self.updateAutoIndent(p, w)
        w.seeInsertPoint()
    #@+node:ekr.20150514063305.275: *4* updateAutoIndent (leoEditCommands)
    def updateAutoIndent(self, p, w):
        '''Handle auto indentation.'''
        trace = False and not g.unitTesting
        c = self.c
        tab_width = c.getTabWidth(p)
        # Get the previous line.
        s = w.getAllText()
        ins = w.getInsertPoint()
        i = g.skip_to_start_of_line(s, ins)
        i, j = g.getLine(s, i - 1)
        s = s[i: j - 1]
        # Add the leading whitespace to the present line.
        junk, width = g.skip_leading_ws_with_indent(s, 0, tab_width)
        # g.trace('width',width,'tab_width',tab_width)
        if s and s[-1] == ':':
            # For Python: increase auto-indent after colons.
            if g.findLanguageDirectives(c, p) == 'python':
                width += abs(tab_width)
        if self.smartAutoIndent:
            # Determine if prev line has unclosed parens/brackets/braces
            bracketWidths = [width]
            tabex = 0
            for i in range(0, len(s)):
                if s[i] == '\t':
                    tabex += tab_width - 1
                if s[i] in '([{':
                    bracketWidths.append(i + tabex + 1)
                elif s[i] in '}])' and len(bracketWidths) > 1:
                    bracketWidths.pop()
            width = bracketWidths.pop()
        ws = g.computeLeadingWhitespace(width, tab_width)
        if ws:
            if trace: g.trace('width: %s, tab_width: %s, ws: %s' % (
                width, tab_width, repr(ws)))
            i = w.getInsertPoint()
            w.insert(i, ws)
            w.setInsertPoint(i + len(ws))
            w.seeInsertPoint()
                # 2011/10/02: Fix cursor-movement bug.
    #@+node:ekr.20150514063305.276: *4* updateAutomatchBracket
    def updateAutomatchBracket(self, p, w, ch, oldSel):
        # assert ch in ('(',')','[',']','{','}')
        c = self.c
        d = c.scanAllDirectives(p)
        i, j = oldSel
        language = d.get('language')
        s = w.getAllText()
        if ch in ('(', '[', '{',):
            automatch = language not in ('plain',)
            if automatch:
                ch = ch + {'(': ')', '[': ']', '{': '}'}.get(ch)
            if i != j: w.delete(i, j)
            w.insert(i, ch)
            if automatch:
                ins = w.getInsertPoint()
                w.setInsertPoint(ins - 1)
        else:
            ins = w.getInsertPoint()
            ch2 = ins < len(s) and s[ins] or ''
            if ch2 in (')', ']', '}'):
                ins = w.getInsertPoint()
                w.setInsertPoint(ins + 1)
            else:
                if i != j: w.delete(i, j)
                w.insert(i, ch)
                w.setInsertPoint(i + 1)
    #@+node:ekr.20150514063305.277: *4* updateTab
    def updateTab(self, p, w, smartTab=True):
        '''Add spaces equivalent to a tab.'''
        trace = False and not g.unitTesting
        c = self.c
        i, j = w.getSelectionRange()
            # Returns insert point if no selection, with i <= j.
        if i != j:
            # w.delete(i,j)
            c.indentBody()
        else:
            tab_width = c.getTabWidth(p)
            # Get the preceeding characters.
            s = w.getAllText()
            start, end = g.getLine(s, i)
            after = s[i: end]
            if after.endswith('\n'): after = after[: -1]
            # Only do smart tab at the start of a blank line.
            doSmartTab = (smartTab and c.smart_tab and i == start)
                # Truly at the start of the line.
                # and not after # Nothing *at all* after the cursor.
            if trace:
                g.trace('smartTab: %s,tab_width: %s, c.tab_width: %s' % (
                    doSmartTab, tab_width, c.tab_width))
                    # 'i %s start %s after %s' % (i,start,repr(after)))
            if doSmartTab:
                self.updateAutoIndent(p, w)
                # Add a tab if otherwise nothing would happen.
                if s == w.getAllText():
                    self.doPlainTab(s, i, tab_width, w)
            else:
                self.doPlainTab(s, i, tab_width, w)
    #@+node:ekr.20150514063305.278: ** insertFileName
    @cmd('insert-file-name')
    def insertFileName(self, event=None):
        '''
        Prompt for a file name, then insert it at the cursor position.
        This operation is undoable if done in the body pane.

        The initial path is made by concatenating path_for_p() and the selected
        text, if there is any, or any path like text immediately preceding the
        cursor.
        '''
        c = self.c
        w = self.editWidget(event)
        if w:

            def callback(arg, w=w):
                i = w.getSelectionRange()[0]
                w.deleteTextSelection()
                w.insert(i, arg)
                if g.app.gui.widget_name(w) == 'body':
                    c.frame.body.onBodyChanged(undoType='Typing')

            # see if the widget already contains the start of a path
            start_text = w.getSelectedText()
            if not start_text:  # look at text preceeding insert point
                start_text = w.getAllText()[:w.getInsertPoint()]
                if start_text:
                    # make non-path characters whitespace
                    start_text = ''.join(i if i not in '\'"`()[]{}<>!|*,@#$&' else ' '
                                         for i in start_text)
                    if start_text[-1].isspace():  # use node path if nothing typed
                        start_text = ''
                    else:
                        start_text = start_text.rsplit(None, 1)[-1]
                        # set selection range so w.deleteTextSelection() works in the callback
                        w.setSelectionRange(
                            w.getInsertPoint()-len(start_text), w.getInsertPoint())

            c.k.functionTail = g.os_path_finalize_join(self.path_for_p(c, c.p), start_text or '')
            c.k.getFileName(event, callback=callback)
    #@+node:tbrown.20151118134307.1: ** path_for_p
    def path_for_p(self, c, p):
        """path_for_p - return the filesystem path (directory) containing
        node `p`.

        FIXME: this general purpose code should be somewhere else, and there
        may already be functions that do some of the work, although perhaps
        without handling so many corner cases (@auto-my-custom-type etc.)

        :param outline c: outline containing p
        :param position p: position to locate
        :return: path
        :rtype: str
        """

        def atfile(p):
            """return True if p is an @<file> node *of any kind*"""
            word0 = p.h.split()[0]
            return (
                word0 in g.app.atFileNames|set(['@auto']) or
                word0.startswith('@auto-')
            )

        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        while c.positionExists(p):
            if atfile(p):  # see if it's a @<file> node of some sort
                nodepath = p.h.split(None, 1)[-1]
                nodepath = g.os_path_join(path, nodepath)
                if not g.os_path_isdir(nodepath):  # remove filename
                    nodepath = g.os_path_dirname(nodepath)
                if g.os_path_isdir(nodepath):  # append if it's a directory
                    path = nodepath
                break
            p.moveToParent()

        return path
    #@+node:ekr.20150514063305.279: ** insertHeadlineTime
    @cmd('insert-headline-time')
    def insertHeadlineTime(self, event=None):
        '''Insert a date/time stamp in the headline of the selected node.'''
        frame = self
        c, p = frame.c, self.c.p
        if g.app.batchMode:
            c.notValidInBatchMode("Insert Headline Time")
            return
        w = c.frame.tree.edit_widget(p)
            # 2015/06/09: Fix bug 131: Insert time in headline now inserts time in body
            # Get the wrapper from the tree itself.
            # Do *not* set w = self.editWidget!
        if w:
            # Fix bug https://bugs.launchpad.net/leo-editor/+bug/1185933
            # insert-headline-time should insert at cursor.
            # Note: The command must be bound to a key for this to work.
            ins = w.getInsertPoint()
            s = c.getTime(body=False)
            w.insert(ins, s)
        else:
            c.endEditing()
            time = c.getTime(body=False)
            s = p.h.rstrip()
            if s:
                p.h = ' '.join([s, time])
            else:
                p.h = time
            c.redrawAndEdit(p, selectAll=True)
    #@+node:ekr.20150514063305.280: ** line...
    #@+node:ekr.20150514063305.281: *3* flushLines
    @cmd('flush-lines')
    def flushLines(self, event):
        '''
        Delete each line that contains a match for regexp, operating on the
        text after point.

        In Transient Mark mode, if the region is active, the command operates
        on the region instead.
        '''
        k = self.c.k
        state = k.getState('flush-lines')
        if state == 0:
            k.setLabelBlue('Flush lines regexp: ')
            k.getArg(event, 'flush-lines', 1, self.flushLines)
        else:
            k.clearState()
            k.resetLabel()
            self.linesHelper(event, k.arg, 'flush')
            k.commandName = 'flush-lines %s' % k.arg
    #@+node:ekr.20150514063305.282: *3* keepLines
    @cmd('keep-lines')
    def keepLines(self, event):
        '''
        Delete each line that does not contain a match for regexp, operating on
        the text after point.

        In Transient Mark mode, if the region is active, the command operates
        on the region instead.
        '''
        k = self.c.k
        state = k.getState('keep-lines')
        if state == 0:
            k.setLabelBlue('Keep lines regexp: ')
            k.getArg(event, 'keep-lines', 1, self.keepLines)
        else:
            k.clearState()
            k.resetLabel()
            self.linesHelper(event, k.arg, 'keep')
            k.commandName = 'keep-lines %s' % k.arg
    #@+node:ekr.20150514063305.283: *3* linesHelper
    def linesHelper(self, event, pattern, which):
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType=which + '-lines')
        if w.hasSelection():
            i, end = w.getSelectionRange()
        else:
            i = w.getInsertPoint()
            end = 'end'
        txt = w.get(i, end)
        tlines = txt.splitlines(True)
        keeplines = list(tlines) if which == 'flush' else []
        try:
            regex = re.compile(pattern)
            for n, z in enumerate(tlines):
                f = regex.findall(z)
                if which == 'flush' and f:
                    keeplines[n] = None
                elif f:
                    keeplines.append(z)
        except Exception:
            return
        if which == 'flush':
            keeplines = [x for x in keeplines if x != None]
        w.delete(i, end)
        w.insert(i, ''.join(keeplines))
        w.setInsertPoint(i)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.284: *3* splitLine
    @cmd('split-line')
    def splitLine(self, event):
        '''Split a line at the cursor position.'''
        w = self.editWidget(event)
        if w:
            self.beginCommand(w, undoType='split-line')
            s = w.getAllText()
            ins = w.getInsertPoint()
            w.setAllText(s[: ins] + '\n' + s[ins:])
            w.setInsertPoint(ins + 1)
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.285: ** move cursor... (leoEditCommands)
    #@+node:ekr.20150514063305.286: *3*  general helpers
    #@+node:ekr.20150514063305.287: *4* extendHelper
    def extendHelper(self, w, extend, spot, upOrDown=False):
        '''
        Handle the details of extending the selection.
        This method is called for all cursor moves.

        extend: Clear the selection unless this is True.
        spot:   The *new* insert point.
        '''
        trace = False and not g.unitTesting
        verbose = False
        c, p = self.c, self.c.p
        extend = extend or self.extendMode
        ins = w.getInsertPoint()
        i, j = w.getSelectionRange()
        if trace: g.trace(
            'extend', extend, 'ins', ins, 'sel=', i, j,
            'spot=', spot, 'moveSpot', self.moveSpot)
        # Reset the move spot if needed.
        if self.moveSpot is None or p.v != self.moveSpotNode:
            if trace: g.trace('no spot')
            self.setMoveCol(w, ins if extend else spot) # sets self.moveSpot.
        elif extend:
            # 2011/05/20: Fix bug 622819
            # Ctrl-Shift movement is incorrect when there is an unexpected selection.
            if i == j:
                if trace: g.trace('extend and no sel')
                self.setMoveCol(w, ins) # sets self.moveSpot.
            elif self.moveSpot in (i, j) and self.moveSpot != ins:
                if trace and verbose: g.trace('extend and movespot matches')
                # The bug fix, part 1.
            else:
                # The bug fix, part 2.
                # Set the moveCol to the *not* insert point.
                if ins == i: k = j
                elif ins == j: k = i
                else: k = ins
                if trace: g.trace('extend and unexpected spot', k)
                self.setMoveCol(w, k) # sets self.moveSpot.
        else:
            if upOrDown:
                s = w.getAllText()
                i2, j2 = g.getLine(s, spot)
                line = s[i2: j2]
                row, col = g.convertPythonIndexToRowCol(s, spot)
                if True: # was j2 < len(s)-1:
                    n = min(self.moveCol, max(0, len(line) - 1))
                else:
                    n = min(self.moveCol, max(0, len(line))) # A tricky boundary.
                # g.trace('using moveCol',self.moveCol,'line',repr(line),'n',n)
                spot = g.convertRowColToPythonIndex(s, row, n)
            else: # Plain move forward or back.
                # g.trace('plain forward/back move')
                self.setMoveCol(w, spot) # sets self.moveSpot.
        if extend:
            if trace: g.trace('range', spot, self.moveSpot)
            if spot < self.moveSpot:
                w.setSelectionRange(spot, self.moveSpot, insert=spot)
            else:
                w.setSelectionRange(self.moveSpot, spot, insert=spot)
        else:
            if trace: g.trace('insert point', spot)
            w.setSelectionRange(spot, spot, insert=spot)
        w.seeInsertPoint()
        c.frame.updateStatusLine()
    #@+node:ekr.20150514063305.288: *4* moveToHelper (leoEditCommands)
    def moveToHelper(self, event, spot, extend):
        '''
        Common helper method for commands the move the cursor
        in a way that can be described by a Tk Text expression.
        '''
        c, k = self.c, self.c.k
        w = self.editWidget(event)
        if not w: return
        c.widgetWantsFocusNow(w)
        # Put the request in the proper range.
        if c.widget_name(w).startswith('mini'):
            i, j = k.getEditableTextRange()
            if spot < i: spot = i
            elif spot > j: spot = j
        self.extendHelper(w, extend, spot, upOrDown=False)
    #@+node:ekr.20150514063305.289: *4* setMoveCol
    def setMoveCol(self, w, spot):
        '''Set the column to which an up or down arrow will attempt to move.'''
        c, p = self.c, self.c.p
        i, row, col = w.toPythonIndexRowCol(spot)
        self.moveSpot = i
        self.moveCol = col
        self.moveSpotNode = p.v
    #@+node:ekr.20150514063305.290: *3* backToHome/ExtendSelection
    @cmd('back-to-home')
    def backToHome(self, event, extend=False):
        '''
        Smart home:
        Position the point at the first non-blank character on the line,
        or the start of the line if already there.
        '''
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        if s:
            i, j = g.getLine(s, ins)
            i1 = i
            while i < j and s[i] in (' \t'):
                i += 1
            if i == ins:
                i = i1
            self.moveToHelper(event, i, extend=extend)

    @cmd('back-to-home-extend-selection')
    def backToHomeExtendSelection(self, event):
        self.backToHome(event, extend=True)
    #@+node:ekr.20150514063305.291: *3* backToIndentation
    @cmd('back-to-indentation')
    def backToIndentation(self, event):
        '''Position the point at the first non-blank character on the line.'''
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        while i < j and s[i] in (' \t'):
            i += 1
        self.moveToHelper(event, i, extend=False)
    #@+node:ekr.20150514063305.292: *3* between lines & helper
    @cmd('next-line')
    def nextLine(self, event):
        '''Move the cursor down, extending the selection if in extend mode.'''
        self.moveUpOrDownHelper(event, 'down', extend=False)

    @cmd('next-line-extend-selection')
    def nextLineExtendSelection(self, event):
        '''Extend the selection by moving the cursor down.'''
        self.moveUpOrDownHelper(event, 'down', extend=True)

    @cmd('previous-line')
    def prevLine(self, event):
        '''Move the cursor up, extending the selection if in extend mode.'''
        self.moveUpOrDownHelper(event, 'up', extend=False)

    @cmd('previous-line-extend-selection')
    def prevLineExtendSelection(self, event):
        '''Extend the selection by moving the cursor up.'''
        self.moveUpOrDownHelper(event, 'up', extend=True)
    #@+node:ekr.20150514063305.293: *4* moveUpOrDownHelper
    def moveUpOrDownHelper(self, event, direction, extend):
        trace = False and not g.unitTesting
        w = self.editWidget(event)
        if not w:
            return
        ins = w.getInsertPoint()
        s = w.getAllText()
        w.seeInsertPoint()
        if hasattr(w, 'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=direction, extend=extend)
        else:
            # Find the start of the next/prev line.
            row, col = g.convertPythonIndexToRowCol(s, ins)
            if trace:
                gui_ins = w.toPythonIndex(ins)
                bbox = w.bbox(gui_ins)
                if bbox:
                    x, y, width, height = bbox
                    # bbox: x,y,width,height:  dlineinfo: x,y,width,height,offset
                    g.trace('gui_ins', gui_ins, 'dlineinfo', w.dlineinfo(gui_ins), 'bbox', bbox)
                    g.trace('ins', ins, 'row', row, 'col', col,
                        'event.x', event and event.x, 'event.y', event and event.y)
                    g.trace('subtracting line height', w.index('@%s,%s' % (x, y - height)))
                    g.trace('adding      line height', w.index('@%s,%s' % (x, y + height)))
            i, j = g.getLine(s, ins)
            if direction == 'down':
                i2, j2 = g.getLine(s, j)
            else:
                i2, j2 = g.getLine(s, i - 1)
            # The spot is the start of the line plus the column index.
            n = max(0, j2 - i2 - 1) # The length of the new line.
            col2 = min(col, n)
            spot = i2 + col2
            if trace: g.trace('spot', spot, 'n', n, 'col', col, 'line', repr(s[i2: j2]))
            self.extendHelper(w, extend, spot, upOrDown=True)
    #@+node:ekr.20150514063305.294: *3* buffers & helper
    @cmd('beginning-of-buffer')
    def beginningOfBuffer(self, event):
        '''Move the cursor to the start of the body text.'''
        self.moveToBufferHelper(event, 'home', extend=False)

    @cmd('beginning-of-buffer-extend-selection')
    def beginningOfBufferExtendSelection(self, event):
        '''Extend the text selection by moving the cursor to the start of the body text.'''
        self.moveToBufferHelper(event, 'home', extend=True)

    @cmd('end-of-buffer')
    def endOfBuffer(self, event):
        '''Move the cursor to the end of the body text.'''
        self.moveToBufferHelper(event, 'end', extend=False)

    @cmd('end-of-buffer-extend-selection')
    def endOfBufferExtendSelection(self, event):
        '''Extend the text selection by moving the cursor to the end of the body text.'''
        self.moveToBufferHelper(event, 'end', extend=True)
    #@+node:ekr.20150514063305.295: *4* moveToBufferHelper
    def moveToBufferHelper(self, event, spot, extend):
        w = self.editWidget(event)
        if not w:
            return
        if hasattr(w, 'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=spot, extend=extend)
        else:
            if spot == 'home':
                self.moveToHelper(event, 0, extend=extend)
            elif spot == 'end':
                s = w.getAllText()
                self.moveToHelper(event, len(s), extend=extend)
            else:
                g.trace('can not happen: bad spot', spot)
    #@+node:ekr.20150514063305.296: *3* characters & helper
    @cmd('back-char')
    def backCharacter(self, event):
        '''Move the cursor back one character, extending the selection if in extend mode.'''
        self.moveToCharacterHelper(event, 'left', extend=False)

    @cmd('back-char-extend-selection')
    def backCharacterExtendSelection(self, event):
        '''Extend the selection by moving the cursor back one character.'''
        self.moveToCharacterHelper(event, 'left', extend=True)

    @cmd('forward-char')
    def forwardCharacter(self, event):
        '''Move the cursor forward one character, extending the selection if in extend mode.'''
        self.moveToCharacterHelper(event, 'right', extend=False)

    @cmd('forward-char-extend-selection')
    def forwardCharacterExtendSelection(self, event):
        '''Extend the selection by moving the cursor forward one character.'''
        self.moveToCharacterHelper(event, 'right', extend=True)
    #@+node:ekr.20150514063305.297: *4* moveToCharacterHelper
    def moveToCharacterHelper(self, event, spot, extend):
        w = self.editWidget(event)
        if not w:
            return
        if hasattr(w, 'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=spot, extend=extend)
        else:
            i = w.getInsertPoint()
            if spot == 'left':
                i = max(0, i - 1)
                self.moveToHelper(event, i, extend=extend)
            elif spot == 'right':
                i = min(i + 1, len(w.getAllText()))
                self.moveToHelper(event, i, extend=extend)
            else:
                g.trace('can not happen: bad spot: %s' % spot)
    #@+node:ekr.20150514063305.298: *3* clear/set/ToggleExtendMode
    @cmd('clear-extend-mode')
    def clearExtendMode(self, event):
        '''Turn off extend mode: cursor movement commands do not extend the selection.'''
        self.extendModeHelper(event, False)

    @cmd('set-extend-mode')
    def setExtendMode(self, event):
        '''Turn on extend mode: cursor movement commands do extend the selection.'''
        self.extendModeHelper(event, True)

    @cmd('toggle-extend-mode')
    def toggleExtendMode(self, event):
        '''Toggle extend mode, i.e., toggle whether cursor movement commands extend the selections.'''
        self.extendModeHelper(event, not self.extendMode)

    def extendModeHelper(self, event, val):
        c = self.c
        w = self.editWidget(event)
        if w:
            self.extendMode = val
            if not g.unitTesting:
                # g.red('extend mode','on' if val else 'off'))
                c.k.showStateAndMode()
            c.widgetWantsFocusNow(w)
    #@+node:ekr.20150514063305.299: *3* exchangePointMark
    @cmd('exchange-point-mark')
    def exchangePointMark(self, event):
        '''Exchange the point (insert point) with the mark (the other end of the selected text).'''
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        if hasattr(w, 'leoMoveCursorHelper'):
            w.leoMoveCursorHelper(kind='exchange', extend=False)
        else:
            c.widgetWantsFocusNow(w)
            i, j = w.getSelectionRange(sort=False)
            if i == j: return
            ins = w.getInsertPoint()
            ins = j if ins == i else i
            w.setInsertPoint(ins)
            w.setSelectionRange(i, j, insert=None)
    #@+node:ekr.20150514063305.300: *3* extend-to-line
    @cmd('extend-to-line')
    def extendToLine(self, event):
        '''Select the line at the cursor.'''
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        n = len(s)
        i = w.getInsertPoint()
        while 0 <= i < n and not s[i] == '\n':
            i -= 1
        i += 1
        i1 = i
        while 0 <= i < n and not s[i] == '\n':
            i += 1
        w.setSelectionRange(i1, i)
    #@+node:ekr.20150514063305.301: *3* extend-to-sentence
    @cmd('extend-to-sentence')
    def extendToSentence(self, event):
        '''Select the line at the cursor.'''
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        n = len(s)
        i = w.getInsertPoint()
        i2 = 1 + s.find('.', i)
        if i2 == -1: i2 = n
        i1 = 1 + s.rfind('.', 0, i2 - 1)
        w.setSelectionRange(i1, i2)
    #@+node:ekr.20150514063305.302: *3* extend-to-word
    @cmd('extend-to-word')
    def extendToWord(self, event, select=True, w=None):
        '''Compute the word at the cursor. Select it if select arg is True.'''
        if not w:
            w = self.editWidget(event)
        if not w:
            return 0, 0
        s = w.getAllText()
        n = len(s)
        i = i1 = w.getInsertPoint()
        # Find a word char on the present line if one isn't at the cursor.
        if not (0 <= i < n and g.isWordChar(s[i])):
            # First, look forward
            while i < n and not g.isWordChar(s[i]) and s[i] != '\n':
                i += 1
            # Next, look backward.
            if not (0 <= i < n and g.isWordChar(s[i])):
                i = i1 - 1 if (i >= n or s[i] == '\n') else i1
                while 0 <= i and not g.isWordChar(s[i]) and s[i] != '\n':
                    i -= 1
        # Make sure s[i] is a word char.
        if 0 <= i < n and g.isWordChar(s[i]):
            # Find the start of the word.
            while 0 <= i < n and g.isWordChar(s[i]):
                i -= 1
            i += 1
            i1 = i
            # Find the end of the word.
            while 0 <= i < n and g.isWordChar(s[i]):
                i += 1
            if select:
                w.setSelectionRange(i1, i)
            return i1, i
        else:
            return 0, 0
    #@+node:ekr.20150514063305.303: *3* movePastClose & helper
    @cmd('move-past-close')
    def movePastClose(self, event):
        '''Move the cursor past the closing parenthesis.'''
        self.movePastCloseHelper(event, extend=False)

    @cmd('move-past-close-extend-selection')
    def movePastCloseExtendSelection(self, event):
        '''Extend the selection by moving the cursor past the closing parenthesis.'''
        self.movePastCloseHelper(event, extend=True)
    #@+node:ekr.20150514063305.304: *4* movePastCloseHelper
    def movePastCloseHelper(self, event, extend):
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        ins = w.getInsertPoint()
        # Scan backwards for i,j.
        i = ins
        while i >= 0 and s[i] != '\n':
            if s[i] == '(': break
            i -= 1
        else: return
        j = ins
        while j >= 0 and s[j] != '\n':
            if s[j] == '(': break
            j -= 1
        if i < j: return
        # Scan forward for i2,j2.
        i2 = ins
        while i2 < len(s) and s[i2] != '\n':
            if s[i2] == ')': break
            i2 += 1
        else: return
        j2 = ins
        while j2 < len(s) and s[j2] != '\n':
            if s[j2] == ')': break
            j2 += 1
        if i2 > j2: return
        self.moveToHelper(event, i2 + 1, extend)
    #@+node:ekr.20150514063305.305: *3* moveWithinLineHelper
    def moveWithinLineHelper(self, event, spot, extend):
        w = self.editWidget(event)
        if not w:
            return
        # Bug fix: 2012/02/28: don't use the Qt end-line logic:
        # it apparently does not work for wrapped lines.
        if hasattr(w, 'leoMoveCursorHelper') and spot != 'end-line':
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=spot, extend=extend)
        else:
            s = w.getAllText()
            ins = w.getInsertPoint()
            i, j = g.getLine(s, ins)
            if spot == 'start-line':
                self.moveToHelper(event, i, extend=extend)
            elif spot == 'end-line':
                # Bug fix: 2011/11/13: Significant in external tests.
                if g.match(s, j - 1, '\n'): j -= 1
                self.moveToHelper(event, j, extend=extend)
            else:
                g.trace('can not happen: bad spot: %s' % spot)
    #@+node:ekr.20150514063305.306: *3* pages & helper
    @cmd('back-page')
    def backPage(self, event):
        '''Move the cursor back one page,
        extending the selection if in extend mode.'''
        self.movePageHelper(event, kind='back', extend=False)

    @cmd('back-page-extend-selection')
    def backPageExtendSelection(self, event):
        '''Extend the selection by moving the cursor back one page.'''
        self.movePageHelper(event, kind='back', extend=True)

    @cmd('forward-page')
    def forwardPage(self, event):
        '''Move the cursor forward one page,
        extending the selection if in extend mode.'''
        self.movePageHelper(event, kind='forward', extend=False)

    @cmd('forward-page-extend-selection')
    def forwardPageExtendSelection(self, event):
        '''Extend the selection by moving the cursor forward one page.'''
        self.movePageHelper(event, kind='forward', extend=True)
    #@+node:ekr.20150514063305.307: *4* movePageHelper
    def movePageHelper(self, event, kind, extend): # kind in back/forward.
        '''Move the cursor up/down one page, possibly extending the selection.'''
        trace = False and not g.unitTesting
        w = self.editWidget(event)
        if not w:
            return
        linesPerPage = 15 # To do.
        if hasattr(w, 'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(
                kind='page-down' if kind == 'forward' else 'page-up',
                extend=extend, linesPerPage=linesPerPage)
            # w.seeInsertPoint()
            # c.frame.updateStatusLine()
            # w.rememberSelectionAndScroll()
        else:
            ins = w.getInsertPoint()
            s = w.getAllText()
            lines = g.splitLines(s)
            row, col = g.convertPythonIndexToRowCol(s, ins)
            row2 = max(0, row - linesPerPage) if kind == 'back' else min(row + linesPerPage, len(lines) - 1)
            if row == row2: return
            spot = g.convertRowColToPythonIndex(s, row2, col, lines=lines)
            if trace: g.trace('spot', spot, 'row2', row2)
            self.extendHelper(w, extend, spot, upOrDown=True)
    #@+node:ekr.20150514063305.308: *3* paragraphs & helpers
    @cmd('back-paragraph')
    def backwardParagraph(self, event):
        '''Move the cursor to the previous paragraph.'''
        self.backwardParagraphHelper(event, extend=False)

    @cmd('back-paragraph-extend-selection')
    def backwardParagraphExtendSelection(self, event):
        '''Extend the selection by moving the cursor to the previous paragraph.'''
        self.backwardParagraphHelper(event, extend=True)

    @cmd('forward-paragraph')
    def forwardParagraph(self, event):
        '''Move the cursor to the next paragraph.'''
        self.forwardParagraphHelper(event, extend=False)

    @cmd('forward-paragraph-extend-selection')
    def forwardParagraphExtendSelection(self, event):
        '''Extend the selection by moving the cursor to the next paragraph.'''
        self.forwardParagraphHelper(event, extend=True)
    #@+node:ekr.20150514063305.309: *4* backwardParagraphHelper
    def backwardParagraphHelper(self, event, extend):
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        i, j = w.getSelectionRange()
        # A hack for wx gui: set the insertion point to the end of the selection range.
        if g.app.unitTesting:
            w.setInsertPoint(j)
        i, j = g.getLine(s, j)
        line = s[i: j]
        if line.strip():
            # Find the start of the present paragraph.
            while i > 0:
                i, j = g.getLine(s, i - 1)
                line = s[i: j]
                if not line.strip(): break
        # Find the end of the previous paragraph.
        while i > 0:
            i, j = g.getLine(s, i - 1)
            line = s[i: j]
            if line.strip():
                i = j - 1
                break
        self.moveToHelper(event, i, extend)
    #@+node:ekr.20150514063305.310: *4* forwardParagraphHelper
    def forwardParagraphHelper(self, event, extend):
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        line = s[i: j]
        if line.strip(): # Skip past the present paragraph.
            self.selectParagraphHelper(w, i)
            i, j = w.getSelectionRange()
            j += 1
        # Skip to the next non-blank line.
        i = j
        while j < len(s):
            i, j = g.getLine(s, j)
            line = s[i: j]
            if line.strip(): break
        w.setInsertPoint(ins) # Restore the original insert point.
        self.moveToHelper(event, i, extend)
    #@+node:ekr.20150514063305.311: *3* selectAllText (leoEditCommands)
    @cmd('select-all')
    def selectAllText(self, event):
        '''Select all text.'''
        c, k = self.c, self.c.k
        w = self.editWidget(event)
        if not w: return
        # Bug fix 2013/12/13: Special case the minibuffer.
        if w == k.w:
            k.selectAll()
        else:
            isTextWrapper = g.isTextWrapper(w)
            if w and isTextWrapper:
                return w.selectAllText()
    #@+node:ekr.20150514063305.312: *3* sentences & helpers
    @cmd('back-sentence')
    def backSentence(self, event):
        '''Move the cursor to the previous sentence.'''
        self.backSentenceHelper(event, extend=False)

    @cmd('back-sentence-extend-selection')
    def backSentenceExtendSelection(self, event):
        '''Extend the selection by moving the cursor to the previous sentence.'''
        self.backSentenceHelper(event, extend=True)

    @cmd('forward-sentence')
    def forwardSentence(self, event):
        '''Move the cursor to the next sentence.'''
        self.forwardSentenceHelper(event, extend=False)

    @cmd('forward-sentence-extend-selection')
    def forwardSentenceExtendSelection(self, event):
        '''Extend the selection by moving the cursor to the next sentence.'''
        self.forwardSentenceHelper(event, extend=True)
    #@+node:ekr.20150514063305.313: *4* backSentenceHelper
    def backSentenceHelper(self, event, extend):
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        ins = w.getInsertPoint()
        # Find the starting point of the scan.
        i = ins
        i -= 1 # Ensure some progress.
        if i < 0:
            return
        # Tricky.
        if s[i] == '.':
            i -= 1
        while i >= 0 and s[i] in ' \n':
            i -= 1
        if i >= ins:
            i -= 1
        if i >= len(s):
            i -= 1
        if i <= 0:
            return
        if s[i] == '.':
            i -= 1
        # Scan backwards to the end of the paragraph.
        # Stop at empty lines.
        # Skip periods within words.
        # Stop at sentences ending in non-periods.
        end = False
        while not end and i >= 0:
            progress = i
            if s[i] == '.':
                # Skip periods surrounded by letters/numbers
                if i > 0 and s[i - 1].isalnum() and s[i + 1].isalnum():
                    i -= 1
                else:
                    i += 1
                    while i < len(s) and s[i] in ' \n':
                        i += 1
                    i -= 1
                    break
            elif s[i] == '\n':
                j = i - 1
                while j >= 0:
                    if s[j] == '\n':
                        # Don't include first newline.
                        end = True
                        break # found blank line.
                    elif s[j] == ' ':
                        j -= 1
                    else:
                        i -= 1
                        break # no blank line found.
                else:
                    # No blank line found.
                    i -= 1
            else:
                i -= 1
            assert end or progress > i
        i += 1
        if i < ins:
            self.moveToHelper(event, i, extend)
    #@+node:ekr.20150514063305.314: *4* forwardSentenceHelper
    def forwardSentenceHelper(self, event, extend):
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        ins = w.getInsertPoint()
        if ins >= len(s):
            return
        # Find the starting point of the scan.
        i = ins
        if i + 1 < len(s) and s[i + 1] == '.':
            i += 1
        if s[i] == '.':
            i += 1
        else:
            while i < len(s) and s[i] in ' \n':
                i += 1
            i -= 1
        if i <= ins:
            i += 1
        if i >= len(s):
            return
        # Scan forward to the end of the paragraph.
        # Stop at empty lines.
        # Skip periods within words.
        # Stop at sentences ending in non-periods.
        end = False
        while not end and i < len(s):
            progress = i
            if s[i] == '.':
                # Skip periods surrounded by letters/numbers
                if 0 < i < len(s) and s[i - 1].isalnum() and s[i + 1].isalnum():
                    i += 1
                else:
                    i += 1
                    break # Include the paragraph.
            elif s[i] == '\n':
                j = i + 1
                while j < len(s):
                    if s[j] == '\n':
                        # Don't include first newline.
                        end = True
                        break # found blank line.
                    elif s[j] == ' ':
                        j += 1
                    else:
                        i += 1
                        break # no blank line found.
                else:
                    # No blank line found.
                    i += 1
            else:
                i += 1
            assert end or progress < i
        i = min(i, len(s))
        if i > ins:
            self.moveToHelper(event, i, extend)
    #@+node:ekr.20150514063305.315: *3* within lines
    @cmd('beginning-of-line')
    def beginningOfLine(self, event):
        '''Move the cursor to the start of the line, extending the selection if in extend mode.'''
        self.moveWithinLineHelper(event, 'start-line', extend=False)

    @cmd('beginning-of-line-extend-selection')
    def beginningOfLineExtendSelection(self, event):
        '''Extend the selection by moving the cursor to the start of the line.'''
        self.moveWithinLineHelper(event, 'start-line', extend=True)

    @cmd('end-of-line')
    def endOfLine(self, event):
        '''Move the cursor to the end of the line, extending the selection if in extend mode.'''
        self.moveWithinLineHelper(event, 'end-line', extend=False)

    @cmd('end-of-line-extend-selection')
    def endOfLineExtendSelection(self, event):
        '''Extend the selection by moving the cursor to the end of the line.'''
        self.moveWithinLineHelper(event, 'end-line', extend=True)
    #@+node:ekr.20150514063305.316: *3* words & helper
    @cmd('back-word')
    def backwardWord(self, event):
        '''Move the cursor to the previous word.'''
        self.moveWordHelper(event, extend=False, forward=False)

    @cmd('back-word-extend-selection')
    def backwardWordExtendSelection(self, event):
        '''Extend the selection by moving the cursor to the previous word.'''
        self.moveWordHelper(event, extend=True, forward=False)

    @cmd('forward-end-word')
    def forwardEndWord(self, event): # New in Leo 4.4.2
        '''Move the cursor to the next word.'''
        self.moveWordHelper(event, extend=False, forward=True, end=True)

    @cmd('forward-end-word-extend-selection')
    def forwardEndWordExtendSelection(self, event): # New in Leo 4.4.2
        '''Extend the selection by moving the cursor to the next word.'''
        self.moveWordHelper(event, extend=True, forward=True, end=True)

    @cmd('forward-word')
    def forwardWord(self, event):
        '''Move the cursor to the next word.'''
        self.moveWordHelper(event, extend=False, forward=True)

    @cmd('forward-word-extend-selection')
    def forwardWordExtendSelection(self, event):
        '''Extend the selection by moving the cursor to the end of the next word.'''
        self.moveWordHelper(event, extend=True, forward=True)

    @cmd('back-word-smart')
    def backwardWordSmart(self, event):
        '''Move the cursor to the beginning of the current or the end of the previous word.'''
        self.moveWordHelper(event, extend=False, forward=False, smart=True)

    @cmd('back-word-smart-extend-selection')
    def backwardWordSmartExtendSelection(self, event):
        '''Extend the selection by moving the cursor to the beginning of the current
        or the end of the previous word.'''
        self.moveWordHelper(event, extend=True, forward=False, smart=True)

    @cmd('forward-word-smart')
    def forwardWordSmart(self, event):
        '''Move the cursor to the end of the current or the beginning of the next word.'''
        self.moveWordHelper(event, extend=False, forward=True, smart=True)

    @cmd('forward-word-smart-extend-selection')
    def forwardWordSmartExtendSelection(self, event):
        '''Extend the selection by moving the cursor to the end of the current
        or the beginning of the next word.'''
        self.moveWordHelper(event, extend=True, forward=True, smart=True)
    #@+node:ekr.20150514063305.317: *4* moveWordHelper
    def moveWordHelper(self, event, extend, forward, end=False, smart=False):
        '''
        Move the cursor to the next/previous word.
        The cursor is placed at the start of the word unless end=True
        '''
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        n = len(s)
        i = w.getInsertPoint()
        # pylint: disable=anomalous-backslash-in-string
        alphanumeric_re = re.compile("\w")
        whitespace_re = re.compile("\s")
        simple_whitespace_re = re.compile("[ \t]")
        #@+others
        #@+node:ekr.20150514063305.318: *5* moveWordHelper functions
        def is_alphanumeric(c):
            return alphanumeric_re.match(c) is not None

        def is_whitespace(c):
            return whitespace_re.match(c) is not None

        def is_simple_whitespace(c):
            return simple_whitespace_re.match(c) is not None

        def is_line_break(c):
            return is_whitespace(c) and not is_simple_whitespace(c)

        def is_special(c):
            return not is_alphanumeric(c) and not is_whitespace(c)

        def seek_until_changed(i, match_function, step):
            while 0 <= i < n and match_function(s[i]):
                i += step
            return i

        def seek_word_end(i):
            return seek_until_changed(i, is_alphanumeric, 1)

        def seek_word_start(i):
            return seek_until_changed(i, is_alphanumeric, -1)

        def seek_simple_whitespace_end(i):
            return seek_until_changed(i, is_simple_whitespace, 1)

        def seek_simple_whitespace_start(i):
            return seek_until_changed(i, is_simple_whitespace, -1)

        def seek_special_end(i):
            return seek_until_changed(i, is_special, 1)

        def seek_special_start(i):
            return seek_until_changed(i, is_special, -1)
        #@-others
        # g.trace('smart',smart,'forward',forward,'end',end)
        if smart:
            if forward:
                if 0 <= i < n:
                    if is_alphanumeric(s[i]):
                        i = seek_word_end(i)
                        i = seek_simple_whitespace_end(i)
                    elif is_simple_whitespace(s[i]):
                        i = seek_simple_whitespace_end(i)
                    elif is_special(s[i]):
                        i = seek_special_end(i)
                        i = seek_simple_whitespace_end(i)
                    else:
                        i += 1 # e.g. for newlines
            else:
                i -= 1 # Shift cursor temporarily by -1 to get easy read access to the prev. char
                if 0 <= i < n:
                    if is_alphanumeric(s[i]):
                        i = seek_word_start(i)
                        # Do not seek further whitespace here
                    elif is_simple_whitespace(s[i]):
                        i = seek_simple_whitespace_start(i)
                    elif is_special(s[i]):
                        i = seek_special_start(i)
                        # Do not seek further whitespace here
                    else:
                        i -= 1 # e.g. for newlines
                i += 1
        else:
            if forward:
                # Unlike backward-word moves, there are two options...
                if end:
                    while 0 <= i < n and not g.isWordChar(s[i]):
                        i += 1
                    while 0 <= i < n and g.isWordChar(s[i]):
                        i += 1
                else:
                    while 0 <= i < n and g.isWordChar(s[i]):
                        i += 1
                    while 0 <= i < n and not g.isWordChar(s[i]):
                        i += 1
            else:
                i -= 1
                while 0 <= i < n and not g.isWordChar(s[i]):
                    i -= 1
                while 0 <= i < n and g.isWordChar(s[i]):
                    i -= 1
                i += 1 # 2015/04/30
        self.moveToHelper(event, i, extend)
    #@+node:ekr.20150514063305.319: ** paragraph...
    #@+node:ekr.20150514063305.320: *3* backwardKillParagraph
    @cmd('backward-kill-paragraph')
    def backwardKillParagraph(self, event):
        '''Kill the previous paragraph.'''
        c, k = self.c, self.c.k
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType='backward-kill-paragraph')
        try:
            self.backwardParagraphHelper(event, extend=True)
            i, j = w.getSelectionRange()
            if i > 0: i = min(i + 1, j)
            c.killBufferCommands.kill(event, i, j, undoType=None)
            w.setSelectionRange(i, i, insert=i)
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.321: *3* fillRegion
    @cmd('fill-region')
    def fillRegion(self, event):
        '''Fill all paragraphs in the selected text.'''
        c, p = self.c, self.c.p
        undoType = 'fill-region'
        w = self.editWidget(event)
        i, j = w.getSelectionRange()
        c.undoer.beforeChangeGroup(p, undoType)
        while 1:
            progress = w.getInsertPoint()
            c.reformatParagraph(event, undoType='reformat-paragraph')
            ins = w.getInsertPoint()
            s = w.getAllText()
            w.setInsertPoint(ins)
            if progress >= ins or ins >= j or ins >= len(s):
                break
        c.undoer.afterChangeGroup(p, undoType)
    #@+node:ekr.20150514063305.322: *3* fillRegionAsParagraph
    @cmd('fill-region-as-paragraph')
    def fillRegionAsParagraph(self, event):
        '''Fill the selected text.'''
        w = self.editWidget(event)
        if not w or not self._chckSel(event):
            return
        self.beginCommand(w, undoType='fill-region-as-paragraph')
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.323: *3* fillParagraph
    @cmd('fill-paragraph')
    def fillParagraph(self, event):
        '''Fill the selected paragraph'''
        w = self.editWidget(event)
        if w:
            # Clear the selection range.
            i, j = w.getSelectionRange()
            w.setSelectionRange(i, i, insert=i)
            self.c.reformatParagraph(event)
    #@+node:ekr.20150514063305.324: *3* killParagraph
    @cmd('kill-paragraph')
    def killParagraph(self, event):
        '''Kill the present paragraph.'''
        c, k = self.c, self.c.k
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType='kill-paragraph')
        try:
            self.extendToParagraph(event)
            i, j = w.getSelectionRange()
            c.killBufferCommands.kill(event, i, j, undoType=None)
            w.setSelectionRange(i, i, insert=i)
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.325: *3* extend-to-paragraph & helper
    @cmd('extend-to-paragraph')
    def extendToParagraph(self, event):
        '''Select the paragraph surrounding the cursor.'''
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i, j = g.getLine(s, ins)
        line = s[i: j]
        # Find the start of the paragraph.
        if line.strip(): # Search backward.
            while i > 0:
                i2, j2 = g.getLine(s, i - 1)
                line = s[i2: j2]
                if line.strip(): i = i2
                else: break # Use the previous line.
        else: # Search forward.
            while j < len(s):
                i, j = g.getLine(s, j)
                line = s[i: j]
                if line.strip(): break
            else: return
        # Select from i to the end of the paragraph.
        self.selectParagraphHelper(w, i)
    #@+node:ekr.20150514063305.326: *4* selectParagraphHelper
    def selectParagraphHelper(self, w, start):
        '''Select from start to the end of the paragraph.'''
        s = w.getAllText()
        i1, j = g.getLine(s, start)
        while j < len(s):
            i, j2 = g.getLine(s, j)
            line = s[i: j2]
            if line.strip(): j = j2
            else: break
        j = max(start, j - 1)
        w.setSelectionRange(i1, j, insert=j)
    #@+node:ekr.20150514063305.327: ** region...
    #@+node:ekr.20150514063305.328: *3* tabIndentRegion (indent-rigidly)
    @cmd('indent-rigidly')
    def tabIndentRegion(self, event):
        '''Insert a hard tab at the start of each line of the selected text.'''
        w = self.editWidget(event)
        if not w or not self._chckSel(event):
            return
        self.beginCommand(w, undoType='indent-rigidly')
        s = w.getAllText()
        i1, j1 = w.getSelectionRange()
        i, junk = g.getLine(s, i1)
        junk, j = g.getLine(s, j1)
        lines = g.splitlines(s[i: j])
        n = len(lines)
        lines = g.joinLines(['\t' + line for line in lines])
        s = s[: i] + lines + s[j:]
        w.setAllText(s)
        # Retain original row/col selection.
        w.setSelectionRange(i1, j1 + n, insert=j1 + n)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.329: *3* countRegion
    @cmd('count-region')
    def countRegion(self, event):
        '''Print the number of lines and characters in the selected text.'''
        k = self.c.k
        w = self.editWidget(event)
        if not w:
            return
        txt = w.getSelectedText()
        lines = 1
        chars = 0
        for z in txt:
            if z == '\n': lines += 1
            else: chars += 1
        k.setLabelGrey('Region has %s lines, %s character%s' % (
            lines, chars, '' if chars == 1 else 's'))
    #@+node:ekr.20150514063305.330: *3* moveLinesDown
    @cmd('move-lines-down')
    def moveLinesDown(self, event):
        '''
        Move all lines containing any selected text down one line,
        moving to the next node if the lines are the last lines of the body.
        '''
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        sel_1, sel_2 = w.getSelectionRange()
        insert_pt = w.getInsertPoint() # 2011/04/01
        i, junk = g.getLine(s, sel_1)
        i2, j = g.getLine(s, sel_2)
        lines = s[i: j]
        # Select from start of the first line to the *start* of the last line.
        # This prevents selection creep.
        # n = i2-i
        # g.trace('moveLinesDown:',repr('%s[[%s|%s|%s]]%s' % (
        #    s[i-20:i], s[i:sel_1], s[sel_1:sel_2], s[sel_2:j], s[j:j+20])))
        self.beginCommand(w, undoType='move-lines-down')
        changed = False
        try:
            if j < len(s):
                next_i, next_j = g.getLine(s, j) # 2011/04/01: was j+1
                next_line = s[next_i: next_j]
                n2 = next_j - next_i
                w.delete(i, next_j)
                if next_line.endswith('\n'):
                    # Simply swap positions with next line
                    new_lines = next_line + lines
                else:
                    # Last line of the body to be moved up doesn't end in a newline
                    # while we have to remove the newline from the line above moving down.
                    new_lines = next_line + '\n' + lines[: -1]
                    n2 += 1
                w.insert(i, new_lines)
                w.setSelectionRange(sel_1 + n2, sel_2 + n2, insert=insert_pt + n2)
                changed = True
                # Fix bug 799695: colorizer bug after move-lines-up into a docstring
                c.recolor_now(incremental=False)
        finally:
            self.endCommand(changed=changed, setLabel=True)
    #@+node:ekr.20150514063305.331: *3* moveLinesUp
    @cmd('move-lines-up')
    def moveLinesUp(self, event):
        '''
        Move all lines containing any selected text up one line,
        moving to the previous node as needed.
        '''
        c = self.c
        w = self.editWidget(event)
        if not w:
            return
        s = w.getAllText()
        sel_1, sel_2 = w.getSelectionRange()
        insert_pt = w.getInsertPoint() # 2011/04/01
        i, junk = g.getLine(s, sel_1)
        i2, j = g.getLine(s, sel_2)
        lines = s[i: j]
        # g.trace('moveLinesUp:',repr('%s[[%s|%s|%s]]%s' % (
        #    s[max(0,i-20):i], s[i:sel_1], s[sel_1:sel_2], s[sel_2:j], s[j:j+20])))
        self.beginCommand(w, undoType='move-lines-up')
        changed = False
        try:
            if i > 0:
                prev_i, prev_j = g.getLine(s, i - 1)
                prev_line = s[prev_i: prev_j]
                n2 = prev_j - prev_i
                w.delete(prev_i, j)
                if lines.endswith('\n'):
                    # Simply swap positions with next line
                    new_lines = lines + prev_line
                else:
                    # Lines to be moved up don't end in a newline while the
                    # previous line going down needs its newline taken off.
                    new_lines = lines + '\n' + prev_line[: -1]
                w.insert(prev_i, new_lines)
                w.setSelectionRange(sel_1 - n2, sel_2 - n2, insert=insert_pt - n2)
                changed = True
                # Fix bug 799695: colorizer bug after move-lines-up into a docstring
                c.recolor_now(incremental=False)
        finally:
            self.endCommand(changed=changed, setLabel=True)
    #@+node:ekr.20150514063305.332: *3* reverseRegion
    @cmd('reverse-region')
    def reverseRegion(self, event):
        '''Reverse the order of lines in the selected text.'''
        w = self.editWidget(event)
        if not w or not self._chckSel(event):
            return
        self.beginCommand(w, undoType='reverse-region')
        s = w.getAllText()
        i1, j1 = w.getSelectionRange()
        i, junk = g.getLine(s, i1)
        junk, j = g.getLine(s, j1)
        txt = s[i: j]
        aList = txt.split('\n')
        aList.reverse()
        txt = '\n'.join(aList) + '\n'
        w.setAllText(s[: i1] + txt + s[j1:])
        ins = i1 + len(txt) - 1
        w.setSelectionRange(ins, ins, insert=ins)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.333: *3* up/downCaseRegion & helper
    @cmd('downcase-region')
    def downCaseRegion(self, event):
        '''Convert all characters in the selected text to lower case.'''
        self.caseHelper(event, 'low', 'downcase-region')

    @cmd('toggle-case-region')
    def toggleCaseRegion(self, event):
        '''Toggle the case of all characters in the selected text.'''
        self.caseHelper(event, 'toggle', 'toggle-case-region')

    @cmd('upcase-region')
    def upCaseRegion(self, event):
        '''Convert all characters in the selected text to UPPER CASE.'''
        self.caseHelper(event, 'up', 'upcase-region')

    def caseHelper(self, event, way, undoType):
        w = self.editWidget(event)
        if not w or not w.hasSelection():
            return
        self.beginCommand(w, undoType=undoType)
        s = w.getAllText()
        i, j = w.getSelectionRange()
        ins = w.getInsertPoint()
        s2 = s[i: j]
        if way == 'low':
            sel = s2.lower()
        elif way == 'up':
            sel = s2.upper()
        else:
            assert way == 'toggle'
            sel = s2.swapcase()
        s2 = s[: i] + sel + s[j:]
        # g.trace('sel',repr(sel),'s2',repr(s2))
        changed = s2 != s
        if changed:
            w.setAllText(s2)
            w.setSelectionRange(i, j, insert=ins)
        self.endCommand(changed=changed, setLabel=True)
    #@+node:ekr.20150514063305.334: ** scrolling...
    #@+node:ekr.20150514063305.335: *3* scrollUp/Down & helper
    @cmd('scroll-down-half-page')
    def scrollDownHalfPage(self, event):
        '''Scroll the presently selected pane down one lline.'''
        self.scrollHelper(event, 'down', 'half-page')

    @cmd('scroll-down-line')
    def scrollDownLine(self, event):
        '''Scroll the presently selected pane down one lline.'''
        self.scrollHelper(event, 'down', 'line')

    @cmd('scroll-down-page')
    def scrollDownPage(self, event):
        '''Scroll the presently selected pane down one page.'''
        self.scrollHelper(event, 'down', 'page')

    @cmd('scroll-up-half-page')
    def scrollUpHalfPage(self, event):
        '''Scroll the presently selected pane down one lline.'''
        self.scrollHelper(event, 'up', 'half-page')

    @cmd('scroll-up-line')
    def scrollUpLine(self, event):
        '''Scroll the presently selected pane up one page.'''
        self.scrollHelper(event, 'up', 'line')

    @cmd('scroll-up-page')
    def scrollUpPage(self, event):
        '''Scroll the presently selected pane up one page.'''
        self.scrollHelper(event, 'up', 'page')
    #@+node:ekr.20150514063305.336: *4* scrollHelper (leoEditCommands)
    def scrollHelper(self, event, direction, distance):
        '''
        Scroll the present pane up or down one page
        kind is in ('up/down-half-page/line/page)
        '''
        w = event and event.w
        if w and hasattr(w, 'scrollDelegate'):
            kind = direction + '-' + distance
            w.scrollDelegate(kind)
    #@+node:ekr.20150514063305.337: *3* scrollOutlineUp/Down/Line/Page
    @cmd('scroll-outline-down-line')
    def scrollOutlineDownLine(self, event=None):
        '''Scroll the outline pane down one line.'''
        c, tree = self.c, self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('down-line')
        elif hasattr(tree.canvas, 'leo_treeBar'):
            a, b = tree.canvas.leo_treeBar.get()
            if b < 1.0: tree.canvas.yview_scroll(1, "unit")

    @cmd('scroll-outline-down-page')
    def scrollOutlineDownPage(self, event=None):
        '''Scroll the outline pane down one page.'''
        c, tree = self.c, self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('down-page')
        elif hasattr(tree.canvas, 'leo_treeBar'):
            a, b = tree.canvas.leo_treeBar.get()
            if b < 1.0: tree.canvas.yview_scroll(1, "page")

    @cmd('scroll-outline-up-line')
    def scrollOutlineUpLine(self, event=None):
        '''Scroll the outline pane up one line.'''
        c, tree = self.c, self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('up-line')
        elif hasattr(tree.canvas, 'leo_treeBar'):
            a, b = tree.canvas.leo_treeBar.get()
            if a > 0.0: tree.canvas.yview_scroll(-1, "unit")

    @cmd('scroll-outline-up-page')
    def scrollOutlineUpPage(self, event=None):
        '''Scroll the outline pane up one page.'''
        c, tree = self.c, self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('up-page')
        elif hasattr(tree.canvas, 'leo_treeBar'):
            a, b = tree.canvas.leo_treeBar.get()
            if a > 0.0: tree.canvas.yview_scroll(-1, "page")
    #@+node:ekr.20150514063305.338: *3* scrollOutlineLeftRight
    @cmd('scroll-outline-left')
    def scrollOutlineLeft(self, event=None):
        '''Scroll the outline left.'''
        c, tree = self.c, self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('left')
        elif hasattr(tree.canvas, 'xview_scroll'):
            tree.canvas.xview_scroll(1, "unit")

    @cmd('scroll-outline-right')
    def scrollOutlineRight(self, event=None):
        '''Scroll the outline left.'''
        c, tree = self.c, self.c.frame.tree
        if hasattr(tree, 'scrollDelegate'):
            tree.scrollDelegate('right')
        elif hasattr(tree.canvas, 'xview_scroll'):
            tree.canvas.xview_scroll(-1, "unit")
    #@+node:ekr.20150514063305.339: ** sort...
    #@@nocolor
    #@@color
    #@+at
    # XEmacs provides several commands for sorting text in a buffer.  All
    # operate on the contents of the region (the text between point and the
    # mark).  They divide the text of the region into many "sort records",
    # identify a "sort key" for each record, and then reorder the records
    # using the order determined by the sort keys.  The records are ordered so
    # that their keys are in alphabetical order, or, for numerical sorting, in
    # numerical order.  In alphabetical sorting, all upper-case letters `A'
    # through `Z' come before lower-case `a', in accordance with the ASCII
    # character sequence.
    # 
    #    The sort commands differ in how they divide the text into sort
    # records and in which part of each record they use as the sort key.
    # Most of the commands make each line a separate sort record, but some
    # commands use paragraphs or pages as sort records.  Most of the sort
    # commands use each entire sort record as its own sort key, but some use
    # only a portion of the record as the sort key.
    # 
    # `M-x sort-lines'
    #      Divide the region into lines and sort by comparing the entire text
    #      of a line.  A prefix argument means sort in descending order.
    # 
    # `M-x sort-paragraphs'
    #      Divide the region into paragraphs and sort by comparing the entire
    #      text of a paragraph (except for leading blank lines).  A prefix
    #      argument means sort in descending order.
    # 
    # `M-x sort-pages'
    #      Divide the region into pages and sort by comparing the entire text
    #      of a page (except for leading blank lines).  A prefix argument
    #      means sort in descending order.
    # 
    # `M-x sort-fields'
    #      Divide the region into lines and sort by comparing the contents of
    #      one field in each line.  Fields are defined as separated by
    #      whitespace, so the first run of consecutive non-whitespace
    #      characters in a line constitutes field 1, the second such run
    #      constitutes field 2, etc.
    # 
    #      You specify which field to sort by with a numeric argument: 1 to
    #      sort by field 1, etc.  A negative argument means sort in descending
    #      order.  Thus, minus 2 means sort by field 2 in reverse-alphabetical
    #      order.
    # 
    # `M-x sort-numeric-fields'
    #      Like `M-x sort-fields', except the specified field is converted to
    #      a number for each line and the numbers are compared.  `10' comes
    #      before `2' when considered as text, but after it when considered
    #      as a number.
    # 
    # `M-x sort-columns'
    #      Like `M-x sort-fields', except that the text within each line used
    #      for comparison comes from a fixed range of columns.  An explanation
    #      is given below.
    # 
    #    For example, if the buffer contains:
    # 
    #      On systems where clash detection (locking of files being edited) is
    #      implemented, XEmacs also checks the first time you modify a buffer
    #      whether the file has changed on disk since it was last visited or
    #      saved.  If it has, you are asked to confirm that you want to change
    #      the buffer.
    # 
    # then if you apply `M-x sort-lines' to the entire buffer you get:
    # 
    #      On systems where clash detection (locking of files being edited) is
    #      implemented, XEmacs also checks the first time you modify a buffer
    #      saved.  If it has, you are asked to confirm that you want to change
    #      the buffer.
    #      whether the file has changed on disk since it was last visited or
    # 
    # where the upper case `O' comes before all lower case letters.  If you
    # apply instead `C-u 2 M-x sort-fields' you get:
    # 
    #      saved.  If it has, you are asked to confirm that you want to change
    #      implemented, XEmacs also checks the first time you modify a buffer
    #      the buffer.
    #      On systems where clash detection (locking of files being edited) is
    #      whether the file has changed on disk since it was last visited or
    # 
    # where the sort keys were `If', `XEmacs', `buffer', `systems', and `the'.
    # 
    #    `M-x sort-columns' requires more explanation.  You specify the
    # columns by putting point at one of the columns and the mark at the other
    # column.  Because this means you cannot put point or the mark at the
    # beginning of the first line to sort, this command uses an unusual
    # definition of `region': all of the line point is in is considered part
    # of the region, and so is all of the line the mark is in.
    # 
    #    For example, to sort a table by information found in columns 10 to
    # 15, you could put the mark on column 10 in the first line of the table,
    # and point on column 15 in the last line of the table, and then use this
    # command.  Or you could put the mark on column 15 in the first line and
    # point on column 10 in the last line.
    # 
    #    This can be thought of as sorting the rectangle specified by point
    # and the mark, except that the text on each line to the left or right of
    # the rectangle moves along with the text inside the rectangle.  *Note
    # Rectangles::.
    #@+node:ekr.20150514063305.340: *3* sortLines commands
    @cmd('reverse-sort-lines-ignoring-case')
    def reverseSortLinesIgnoringCase(self, event):
        '''Sort the selected lines in reverse order, ignoring case.'''
        return self.sortLines(event, ignoreCase=True, reverse=True)

    @cmd('reverse-sort-lines')
    def reverseSortLines(self, event):
        '''Sort the selected lines in reverse order.'''
        return self.sortLines(event, reverse=True)

    @cmd('sort-lines-ignoring-case')
    def sortLinesIgnoringCase(self, event):
        '''Sort the selected lines, ignoring case.'''
        return self.sortLines(event, ignoreCase=True)

    @cmd('sort-lines')
    def sortLines(self, event, ignoreCase=False, reverse=False):
        '''Sort the selected lines.'''
        trace = False and not g.unitTesting
        w = self.editWidget(event)
        if not self._chckSel(event):
            if trace: g.trace('early return')
            return
        undoType = 'reverse-sort-lines' if reverse else 'sort-lines'
        self.beginCommand(w, undoType=undoType)
        try:
            s = w.getAllText()
            sel1, sel2 = w.getSelectionRange()
            ins = w.getInsertPoint()
            i, junk = g.getLine(s, sel1)
            junk, j = g.getLine(s, sel2)
            s2 = s[i: j]
            if not s2.endswith('\n'): s2 = s2 + '\n'
            aList = g.splitLines(s2)

            def lower(s):
                return s.lower() if ignoreCase else s

            aList.sort(key=lower)
                # key is a function that extracts args.
            if reverse:
                aList.reverse()
            s = g.joinLines(aList)
            if trace: g.trace(s)
            w.delete(i, j)
            w.insert(i, s)
            w.setSelectionRange(sel1, sel2, insert=ins)
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.341: *3* sortColumns
    @cmd('sort-columns')
    def sortColumns(self, event):
        '''
        Sort lines of selected text using only lines in the given columns to do
        the comparison.
        '''
        w = self.editWidget(event)
        if not self._chckSel(event):
            return
        self.beginCommand(w, undoType='sort-columns')
        try:
            s = w.getAllText()
            sel_1, sel_2 = w.getSelectionRange()
            sint1, sint2 = g.convertPythonIndexToRowCol(s, sel_1)
            sint3, sint4 = g.convertPythonIndexToRowCol(s, sel_2)
            sint1 += 1
            sint3 += 1
            i, junk = g.getLine(s, sel_1)
            junk, j = g.getLine(s, sel_2)
            txt = s[i: j]
            columns = [w.get('%s.%s' % (z, sint2), '%s.%s' % (z, sint4))
                for z in range(sint1, sint3 + 1)]
            aList = g.splitLines(txt)
            zlist = list(zip(columns, aList))
            zlist.sort()
            s = g.joinLines([z[1] for z in zlist])
            w.delete(i, j)
            w.insert(i, s)
            w.setSelectionRange(sel_1, sel_1 + len(s), insert=sel_1 + len(s))
        finally:
            self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.342: *3* sortFields
    @cmd('sort-fields')
    def sortFields(self, event, which=None):
        '''
        Divide the selected text into lines and sort by comparing the contents
        of one field in each line. Fields are defined as separated by
        whitespace, so the first run of consecutive non-whitespace characters
        in a line constitutes field 1, the second such run constitutes field 2,
        etc.

        You specify which field to sort by with a numeric argument: 1 to sort
        by field 1, etc. A negative argument means sort in descending order.
        Thus, minus 2 means sort by field 2 in reverse-alphabetical order.
         '''
        w = self.editWidget(event)
        if not w or not self._chckSel(event):
            return
        self.beginCommand(w, undoType='sort-fields')
        s = w.getAllText()
        ins = w.getInsertPoint()
        r1, r2, r3, r4 = self.getRectanglePoints(w)
        i, junk = g.getLine(s, r1)
        junk, j = g.getLine(s, r4)
        txt = s[i: j] # bug reported by pychecker.
        txt = txt.split('\n')
        fields = []
        fn = r'\w+'
        frx = re.compile(fn)
        for line in txt:
            f = frx.findall(line)
            if not which:
                fields.append(f[0])
            else:
                i = int(which)
                if len(f) < i: return
                i = i - 1
                fields.append(f[i])
        nz = zip(fields, txt)
        nz.sort()
        w.delete(i, j)
        int1 = i
        for z in nz:
            w.insert('%s.0' % int1, '%s\n' % z[1])
            int1 = int1 + 1
        w.setInsertPoint(ins)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.343: ** swap/transpose...
    #@+node:ekr.20150514063305.344: *3* transposeLines
    @cmd('transpose-lines')
    def transposeLines(self, event):
        '''Transpose the line containing the cursor with the preceding line.'''
        w = self.editWidget(event)
        if not w:
            return
        ins = w.getInsertPoint()
        s = w.getAllText()
        if not s.strip():
            return
        i, j = g.getLine(s, ins)
        line1 = s[i: j]
        self.beginCommand(w, undoType='transpose-lines')
        if i == 0: # Transpose the next line.
            i2, j2 = g.getLine(s, j + 1)
            line2 = s[i2: j2]
            w.delete(0, j2)
            w.insert(0, line2 + line1)
            w.setInsertPoint(j2 - 1)
        else: # Transpose the previous line.
            i2, j2 = g.getLine(s, i - 1)
            line2 = s[i2: j2]
            w.delete(i2, j)
            w.insert(i2, line1 + line2)
            w.setInsertPoint(j - 1)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.345: *3* transposeWords
    @cmd('transpose-words')
    def transposeWords(self, event):
        '''Transpose the word at the cursor with the preceding or following word.'''
        trace = False and not g.unitTesting
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType='transpose-words')
        s = w.getAllText()
        i1, j1 = self.extendToWord(event, select=False)
        s1 = s[i1: j1]
        if trace: g.trace(i1, j1, s1)
        if i1 > j1: i1, j1 = j1, i1
        # First, search backward.
        k = i1 - 1
        while k >= 0 and s[k].isspace():
            k -= 1
        changed = k > 0
        if changed:
            ws = s[k + 1: i1]
            if trace: g.trace(repr(ws))
            w.setInsertPoint(k + 1)
            i2, j2 = self.extendToWord(event, select=False)
            s2 = s[i2: j2]
            if trace: g.trace(i2, j2, repr(s2))
            s3 = s[: i2] + s1 + ws + s2 + s[j1:]
            w.setAllText(s3)
            if trace: g.trace(s3)
            w.setSelectionRange(j1, j1, insert=j1)
        else:
            # Next search forward.
            k = j1 + 1
            while k < len(s) and s[k].isspace():
                k += 1
            changed = k < len(s)
            if changed:
                ws = s[j1: k]
                if trace: g.trace(repr(ws))
                w.setInsertPoint(k + 1)
                i2, j2 = self.extendToWord(event, select=False)
                s2 = s[i2: j2]
                if trace: g.trace(i2, j2, repr(s2))
                s3 = s[: i1] + s2 + ws + s1 + s[j2:]
                w.setAllText(s3)
                if trace: g.trace(s3)
                w.setSelectionRange(j1, j1, insert=j1)
        self.endCommand(changed=changed, setLabel=True)
    #@+node:ekr.20150514063305.346: *3* swapCharacters & transeposeCharacters
    @cmd('transpose-chars')
    def transposeCharacters(self, event):
        '''Swap the characters at the cursor.'''
        w = self.editWidget(event)
        if not w:
            return
        self.beginCommand(w, undoType='swap-characters')
        s = w.getAllText()
        i = w.getInsertPoint()
        if 0 < i < len(s):
            w.setAllText(s[: i - 1] + s[i] + s[i - 1] + s[i + 1:])
            w.setSelectionRange(i, i, insert=i)
        self.endCommand(changed=True, setLabel=True)

    swapCharacters = transposeCharacters
    #@+node:ekr.20150514063305.347: ** tabify & untabify (leoEditCommands)
    @cmd('tabify')
    def tabify(self, event):
        '''Convert 4 spaces to tabs in the selected text.'''
        self.tabifyHelper(event, which='tabify')

    @cmd('untabify')
    def untabify(self, event):
        '''Convert tabs to 4 spaces in the selected text.'''
        self.tabifyHelper(event, which='untabify')

    def tabifyHelper(self, event, which):
        w = self.editWidget(event)
        if not w or not w.hasSelection():
            return
        self.beginCommand(w, undoType=which)
        i, end = w.getSelectionRange()
        txt = w.getSelectedText()
        if which == 'tabify':
            pattern = re.compile(' {4,4}') # Huh?
            ntxt = pattern.sub('\t', txt)
        else:
            pattern = re.compile('\t')
            ntxt = pattern.sub('    ', txt)
        w.delete(i, end)
        w.insert(i, ntxt)
        n = i + len(ntxt)
        w.setSelectionRange(n, n, insert=n)
        self.endCommand(changed=True, setLabel=True)
    #@+node:ekr.20150514063305.348: ** uA's (leoEditCommands)
    #@+node:ekr.20150514063305.349: *3* clearNodeUas & clearAllUas
    @cmd('clear-node-uas')
    def clearNodeUas(self, event=None):
        '''Clear the uA's in the selected VNode.'''
        if self.c.p:
            self.c.p.v.u = {}

    @cmd('clear-all-uas')
    def clearAllUas(self, event=None):
        '''Clear all uAs in the entire outline.'''
        for v in self.c.all_unique_nodes():
            v.u = {}
    #@+node:ekr.20150514063305.350: *3* printUas & printAllUas
    @cmd('print-all-uas')
    def printAllUas(self, event=None):
        '''Print all uA's in the outline.'''
        g.es_print('Dump of uAs...')
        for v in self.c.all_unique_nodes():
            if v.u:
                self.printUas(v=v)

    @cmd('print-node-uas')
    def printUas(self, event=None, v=None):
        '''Print the uA's in the selected node.'''
        c = self.c
        if v: d, h = v.u, v.h
        else: d, h = c.p.v.u, c.p.h
        g.es_print(h)
        keys = list(d.keys())
        keys.sort()
        n = 4
        for key in keys:
            n = max(len(key), n)
        for key in keys:
            pad = ' ' * (len(key) - n)
            g.es_print('    %s%s: %s' % (pad, key, d.get(key)))
    #@+node:ekr.20150514063305.351: *3* setUa
    @cmd('set-ua')
    def setUa(self, event):
        '''Prompt for the name and value of a uA, then set the uA in the present node.'''
        c, k = self.c, self.c.k
        tag = 'set-ua'
        state = k.getState(tag)
        if state == 0:
            self.w = self.editWidget(event)
            if self.w:
                k.setLabelBlue('Set uA: ')
                k.getArg(event, tag, 1, self.setUa)
        elif state == 1:
            self.uaName = k.arg
            s = 'Set uA: %s To: ' % (self.uaName)
            k.setLabelBlue(s)
            k.getArg(event, tag, 2, self.setUa, completion=False)
        else:
            assert state == 2, state
            val = k.arg
            d = c.p.v.u
            d[self.uaName] = val
            self.printUas()
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
    #@-others
#@-leo
