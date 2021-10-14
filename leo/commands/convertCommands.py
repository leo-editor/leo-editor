# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20160316095222.1: * @file ../commands/convertCommands.py
#@@first
"""Leo's file-conversion commands."""

import re
import textwrap
from typing import Any, Dict, List
from leo.core import leoGlobals as g
from leo.core import leoBeautify
from leo.commands.baseCommands import BaseEditCommandsClass

def cmd(name):
    """Command decorator for the ConvertCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'convertCommands',])

#@+<< class To_Python >>
#@+node:ekr.20150514063305.123: ** << class To_Python >>
class To_Python:
    """The base class for x-to-python commands."""
    #@+others
    #@+node:ekr.20150514063305.125: *3* To_Python.ctor
    def __init__(self, c):
        """Ctor for To_Python class."""
        self.c = c
        self.p = self.c.p.copy()
        aList = g.get_directives_dict_list(self.p)
        self.tab_width = g.scanAtTabwidthDirectives(aList) or 4
    #@+node:ekr.20150514063305.126: *3* To_Python.go
    def go(self):
        import time
        t1 = time.time()
        c = self.c
        u, undoType = c.undoer, 'typescript-to-python'
        pp = leoBeautify.CPrettyPrinter(c)
        u.beforeChangeGroup(c.p, undoType)
        changed = False
        n_files, n_nodes = 0, 0
        special = ('class ', 'module ', '@file ', '@@file ')
        files = ('@file ', '@@file ')
        for p in self.p.self_and_subtree(copy=False):
            if p.b:
                n_nodes += 1
                if any(p.h.startswith(z) for z in special):
                    g.es_print(p.h)
                    if any(p.h.startswith(z) for z in files):
                        n_files += 1
                bunch = u.beforeChangeNodeContents(p)
                s = pp.indent(p, giveWarnings=False)
                aList = list(s)
                self.convertCodeList(aList)
                s = ''.join(aList)
                if s != p.b:
                    p.b = s
                    p.setDirty()
                    u.afterChangeNodeContents(p, undoType, bunch)
                    changed = True
        # Call this only once, at end.
        if changed:
            u.afterChangeGroup(c.p, undoType, reportFlag=False)
        t2 = time.time()
        g.es_print(f"done! {n_files} files, {n_nodes} nodes, {t2 - t1:2.2f} sec")
    #@+node:ekr.20150514063305.127: *3* To_Python.convertCodeList
    def convertCodeList(self, aList):
        """The main search/replace method."""
        g.trace('must be defined in subclasses.')
    #@+node:ekr.20150514063305.128: *3* To_Python.Utils
    #@+node:ekr.20150514063305.129: *4* match...
    #@+node:ekr.20150514063305.130: *5* match
    def match(self, s, i, pat):
        """
        Return True if s[i:] matches the pat string.

        We can't use g.match because s is usually a list.
        """
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
        """
        Return True if s[i:] word matches the pat string.

        We can't use g.match_word because s is usually a list
        and g.match_word uses s.find.
        """
        if self.match(s, i, pat):
            j = i + len(pat)
            if j >= len(s):
                return True
            if not pat[-1].isalnum():
                # Bug fix 10/16/2012: The pattern terminates the word.
                return True
            ch = s[j]
            return not ch.isalnum() and ch != '_'
        return False
    #@+node:ekr.20150514063305.132: *4* insert_not
    def insert_not(self, aList):
        """Change "!" to "not" except before an equal sign."""
        i = 0
        while i < len(aList):
            if self.is_string_or_comment(aList, i):
                i = self.skip_string_or_comment(aList, i)
            elif aList[i] == '!' and not self.match(aList, i + 1, '='):
                aList[i : i + 1] = list('not ')
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
        return -1 < n1 < n2 and s[n1 + 2 : n2].strip()
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
                del aList[i : j + 1]
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
                break  # safe
            elif self.match(aList, i, '\n'):
                break
            elif self.match(aList, i, ' ') or self.match(aList, i, '\t'):
                # Replace all whitespace by one blank.
                j = self.skip_ws(aList, i)
                assert j > i
                aList[i:j] = [' ']
                i += 1  # make sure we don't go past a newline!
            else: i += 1
        return i
    #@+node:ekr.20150514063305.142: *5* removeMatchingBrackets
    def removeMatchingBrackets(self, aList, i):
        j = self.skip_to_matching_bracket(aList, i)
        if i < j < len(aList):
            c = aList[j]
            if c == ')' or c == ']' or c == '}':
                del aList[j : j + 1]
                del aList[i : i + 1]
                return j - 1
            return j + 1
        return j
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
                assert j < i
                if i >= len(aList) or aList[i] == '\n':
                    # print "removing trailing ws:", `i-j`
                    del aList[j:i]
                    i = j
            else: i += 1
    #@+node:ekr.20150514063305.145: *4* replace... & safe_replace
    #@+node:ekr.20150514063305.146: *5* replace
    def replace(self, aList, findString, changeString):
        """
        Replaces all occurances of findString by changeString.
        changeString may be the empty string, but not None.
        """
        if not findString:
            return
        changeList = list(changeString)
        i = 0
        while i < len(aList):
            if self.match(aList, i, findString):
                aList[i : i + len(findString)] = changeList
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
                aList[i : i + 2] = ['#']
                j = self.skip_past_line(aList, i)
            elif self.match(aList, i, "/*"):
                j = self.skip_c_block_comment(aList, i)
                k = i
                while k - 1 >= 0 and aList[k - 1] in ' \t':
                    k -= 1
                assert k == 0 or aList[k - 1] not in ' \t'
                lws = ''.join(aList[k:i])
                comment_body = ''.join(aList[i + 2 : j - 2])
                comment_lines = g.splitLines(lws + comment_body)
                comment_lines = self.munge_block_comment(comment_lines)
                comment = '\n'.join(comment_lines)  # A list of lines.
                comment_list = list(comment)  # A list of characters.
                aList[k:j] = comment_list
                j = k + len(comment_list)
                progress = j - 1  # Disable the check below.
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

        n = len(comment_lines)
        assert n > 0
        s = comment_lines[0]
        junk, w = g.skip_leading_ws_with_indent(s, 0, tab_width=4)
        if n == 1:
            return [f"{' ' * (w - 1)}# {s.strip()}"]
        junk, w = g.skip_leading_ws_with_indent(s, 0, tab_width=4)
        result = []
        for i, s in enumerate(comment_lines):
            if s.strip():
                result.append(f"{' ' * w}# {s.strip()}")
            elif i == n - 1:
                pass  # Omit the line entirely.
            else:
                result.append('')  # Add a blank line
        return result
    #@+node:ekr.20150514063305.149: *5* replaceSectionDefs
    def replaceSectionDefs(self, aList):
        """Replaces < < x > > = by @c (at the start of lines)."""
        if not aList:
            return
        i = 0
        j = self.is_section_def(aList[i])
        if j > 0:
            aList[i:j] = list("@c ")
        while i < len(aList):
            if self.is_string_or_comment(aList, i):
                i = self.skip_string_or_comment(aList, i)
            elif self.match(aList, i, "\n"):
                i += 1
                j = self.is_section_def(aList[i])
                if j > i:
                    aList[i:j] = list("@c ")
            else: i += 1
    #@+node:ekr.20150514063305.150: *5* safe_replace
    def safe_replace(self, aList, findString, changeString):
        """
        Replaces occurances of findString by changeString,
        but only outside of C comments and strings.
        changeString may be the empty string, but not None.
        """
        if not findString:
            return
        changeList = list(changeString)
        i = 0
        if findString[0].isalpha():  # use self.match_word
            while i < len(aList):
                if self.is_string_or_comment(aList, i):
                    i = self.skip_string_or_comment(aList, i)
                elif self.match_word(aList, i, findString):
                    aList[i : i + len(findString)] = changeList
                    i += len(changeList)
                else:
                    i += 1
        else:  #use self.match
            while i < len(aList):
                if self.match(aList, i, findString):
                    aList[i : i + len(findString)] = changeList
                    i += len(changeList)
                else:
                    i += 1
    #@+node:ekr.20150514063305.151: *4* skip
    #@+node:ekr.20150514063305.152: *5* skip_c_block_comment
    def skip_c_block_comment(self, s, i):
        assert self.match(s, i, "/*")
        i += 2
        while i < len(s):
            if self.match(s, i, "*/"):
                return i + 2
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
        assert s[i].isalpha() or s[i] == '~'
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
        delim = s[i]  # handle either single or double-quoted strings
        assert delim == '"' or delim == "'"
        i += 1
        while i < len(s):
            if s[i] == delim:
                return i + 1
            if s[i] == '\\':
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
            assert False
        return j
    #@+node:ekr.20150514063305.158: *5* skip_to_matching_bracket
    def skip_to_matching_bracket(self, s, i):
        ch = s[i]
        if ch == '(':
            delim = ')'
        elif ch == '{':
            delim = '}'
        elif ch == '[':
            delim = ']'
        else:
            assert False
        i += 1
        while i < len(s):
            ch = s[i]
            if self.is_string_or_comment(s, i):
                i = self.skip_string_or_comment(s, i)
            elif ch == delim:
                return i
            elif ch == '(' or ch == '[' or ch == '{':
                i = self.skip_to_matching_bracket(s, i)
                i += 1  # skip the closing bracket.
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
#@+node:ekr.20210830070921.1: ** function: convert_at_test_nodes
def convert_at_test_nodes(c, converter, root, copy_tree=False):
    """
    Use converter.convert() to convert all the @test nodes in the
    root's tree to children a new last top-level node.
    """
    if not root:
        print('no root')
        return
    last = c.lastTopLevel()
    target = last.insertAfter()
    target.h = 'Converted nodes'
    count = 0
    for p in root.subtree():
        if p.h.startswith('@test'):
            converter.convert_node(c, p, target)
            if copy_tree and p.hasChildren():
                converter.copy_children(c, p, target.lastChild())
            count += 1
    target.expand()
    c.redraw(target)
    print(f"converted {count} @test nodes")
#@+node:ekr.20160316111303.1: ** class ConvertCommandsClass
class ConvertCommandsClass(BaseEditCommandsClass):
    """Leo's file-conversion commands"""

    def __init__(self, c):
        """Ctor for EditCommandsClass class."""
        # pylint: disable=super-init-not-called
        self.c = c
    #@+others
    #@+node:ekr.20160316091843.1: *3* ccc.c-to-python
    @cmd('c-to-python')
    def cToPy(self, event):
        """
        The c-to-python command converts c or c++ text to python text.
        The conversion is not perfect, but it eliminates a lot of tedious
        text manipulation.
        """
        self.C_To_Python(self.c).go()
        self.c.bodyWantsFocus()
    #@+node:ekr.20150514063305.160: *4* class C_To_Python (To_Python)
    class C_To_Python(To_Python):
        #@+others
        #@+node:ekr.20150514063305.161: *5* ctor & helpers (C_To_Python)
        def __init__(self, c):
            """Ctor for C_To_Python class."""
            super().__init__(c)
            #
            # Internal state...
            self.class_name = ''
                # The class name for the present function.  Used to modify ivars.
            self.ivars = []
                # List of ivars to be converted to self.ivar
            self.get_user_types()
        #@+node:ekr.20150514063305.162: *6* get_user_types (C_To_Python)
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
        #@+node:ekr.20150514063305.163: *6* parse_ivars_data
        def parse_ivars_data(self, aList):
            d: Dict[str, List[str]] = {}
            key = None
            aList = [z.strip() for z in aList if z.strip()]
            for s in aList:
                if s.endswith(':'):
                    key = s[:-1].strip()
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
            self.replaceComments(aList)  # should follow all calls to safe_replace
            self.removeTrailingWs(aList)
            r(aList, "\t ", "\t")  # happens when deleting declarations.
        #@+node:ekr.20150514063305.165: *6* handle_all_keywords
        def handle_all_keywords(self, aList):
            """
            converts if ( x ) to if x:
            converts while ( x ) to while x:
            """
            i = 0
            while i < len(aList):
                if self.is_string_or_comment(aList, i):
                    i = self.skip_string_or_comment(aList, i)
                elif (
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
            else:
                assert False
            # Make sure one space follows the keyword.
            k = i
            i = self.skip_ws(aList, i)
            if k == i:
                c = aList[i]
                aList[i : i + 1] = [' ', c]
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
                if i < j < len(aList):
                    ch = aList[j]
                    aList[j : j + 1] = [ch, ":", " "]
                    j = j + 2
                return j
            return i
        #@+node:ekr.20150514063305.167: *6* mungeAllFunctions
        def mungeAllFunctions(self, aList):
            """Scan for a '{' at the top level that is preceeded by ')' """
            prevSemi = 0  # Previous semicolon: header contains all previous text
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
                    firstOpen = None  # restart the scan
                else:
                    j = i + 1
                # Handle unusual cases.
                if j <= progress:
                    j = progress + 1
                assert j > progress
                i = j
        #@+node:ekr.20150514063305.168: *7* handlePossibleFunctionHeader
        def handlePossibleFunctionHeader(self, aList, i, prevSemi, firstOpen):
            """
            Converts function header lines from c++ format to python format.
            That is, converts
                x1..nn w::y ( t1 z1,..tn zn) {
            to
                def y (z1,..zn): {
            """
            assert self.match(aList, i, "{")
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
            assert aList[open_paren] == '('
            head = aList[prevSemi:open_paren]
            # do nothing if the head starts with "if", "for" or "while"
            k = self.skip_ws(head, 0)
            if k >= len(head) or not head[k].isalpha():
                return 1 + self.skip_to_matching_bracket(aList, i)
            kk = self.skip_past_word(head, k)
            if kk > k:
                headString = ''.join(head[k:kk])
                # C keywords that might be followed by '{'
                # print "headString:", headString
                if headString in [
                    "class", "do", "for", "if", "struct", "switch", "while"]:
                    return 1 + self.skip_to_matching_bracket(aList, i)
            args = aList[open_paren : close + 1]
            k = 1 + self.skip_to_matching_bracket(aList, i)
            body = aList[close + 1 : k]
            head = self.massageFunctionHead(head)
            args = self.massageFunctionArgs(args)
            body = self.massageFunctionBody(body)
            result = []
            if head:
                result.extend(head)
            if args:
                result.extend(args)
            if body:
                result.extend(body)
            aList[prevSemi:k] = result
            return prevSemi + len(result)
        #@+node:ekr.20150514063305.169: *7* massageFunctionArgs
        def massageFunctionArgs(self, args):
            assert args[0] == '('
            assert args[-1] == ')'
            result = ['(']
            lastWord = []
            if self.class_name:
                for item in list("self,"):
                    result.append(item)  #can put extra comma
            i = 1
            while i < len(args):
                i = self.skip_ws_and_nl(args, i)
                ch = args[i]
                if ch.isalpha():
                    j = self.skip_past_word(args, i)
                    lastWord = args[i:j]
                    i = j
                elif ch == ',' or ch == ')':
                    for item in lastWord:
                        result.append(item)
                    if lastWord != [] and ch == ',':
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
            result: List[Any] = []
            prevWord = []
            self.class_name = ''
            i = 0
            while i < len(head):
                i = self.skip_ws_and_nl(head, i)
                if i < len(head) and head[i].isalpha():
                    result = []
                    j = self.skip_past_word(head, i)
                    prevWord = head[i:j]
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
                            if head[i:j] == prevWord:
                                result.extend('__init__')
                            elif head[i] == '~' and head[i + 1 : j] == prevWord:
                                result.extend('__del__')
                            else:
                                # result.extend(list('::'))
                                result.extend(head[i:j])
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
            """Look for '{' preceded by '{' or '}' or ';'
            (with intervening whitespace and comments).
            """
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
                        if k == j:
                            break
                        assert k < j
                    if self.match(body, j, '{'):
                        k = j
                        j = self.skip_to_matching_bracket(body, j)
                        m = '# <Start dedented block>...'
                        body[k : k + 1] = list(m)
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
                                    del body[k - spaces : k]
                                    k -= spaces
                                    j -= spaces
                            else:
                                k += 1
                            assert progress < k
                        m = '    # <End dedented block>'
                        body[j : j + 1] = list(m)
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
                    word = ''.join(body[i:j])
                    # print "looking up:", word
                    if word in ivars:
                        # replace word by self.word
                        # print "replacing", word, " by self.", word
                        word = "self." + word
                        word = list(word)  # type:ignore
                        body[i:j] = word
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
                        word = ''.join(body[i:j])
                        i = j
                        if word in self.class_list or word in self.type_list:
                            i = self.skip_ws(body, i)
                            while self.match(body, i, '*'):
                                i += 1
                            i = self.skip_ws(body, i)
                            if self.match(body, i, ')'):
                                i += 1
                                # print "removing cast:", ''.join(body[start:i])
                                del body[start:i]
                                i = start
                else: i += 1
            return body
        #@+node:ekr.20150514063305.175: *8* removeTypeNames
        def removeTypeNames(self, body):
            """Do _not_ remove type names when preceeded by new."""
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
                    word = ''.join(body[i:j])
                    if word in self.class_list or word in self.type_list:
                        j = self.skip_ws(body, j)
                        while self.match(body, j, '*'):
                            j += 1
                        # print "Deleting type name:", ''.join(body[i:j])
                        j = self.skip_ws(body, j)
                        del body[i:j]
                    else:
                        i = j
                else: i += 1
            return body
        #@-others
    #@+node:ekr.20160111190632.1: *3* ccc.makeStubFiles
    @cmd('make-stub-files')
    def make_stub_files(self, event):
        """
        Make stub files for all nearby @<file> nodes.
        Take configuration settings from @x stub-y nodes.
        """
        #@+others
        #@+node:ekr.20160213070235.1: *4* class MakeStubFileAdapter
        class MakeStubFileAdapter:
            """
            An class that adapts leo/external/make_stub_files.py to Leo.

            Settings are taken from Leo settings nodes, not a .cfg file.
            """
            #@+others
            #@+node:ekr.20160213070235.2: *5* msf.ctor & helpers
            def __init__(self, c):
                """MakeStubFile.ctor. From StandAloneMakeStubFile.ctor."""
                self.c = c
                self.msf = msf = g.import_module('make_stub_files')
                x = msf.StandAloneMakeStubFile()
                    # x is used *only* to init ivars.
                # Ivars set on the command line...
                self.config_fn = None
                self.enable_unit_tests = False
                self.files = []  # May also be set in the config file.
                self.output_directory = self.finalize(
                    c.config.getString('stub-output-directory') or '.')
                self.output_fn = None
                self.overwrite = c.config.getBool('stub-overwrite', default=False)
                self.trace_matches = c.config.getBool(
                    'stub-trace-matches', default=False)
                self.trace_patterns = c.config.getBool(
                    'stub-trace-patterns', default=False)
                self.trace_reduce = c.config.getBool('stub-trace-reduce', default=False)
                self.trace_visitors = c.config.getBool(
                    'stub-trace-visitors', default=False)
                self.update_flag = c.config.getBool('stub-update', default=False)
                self.verbose = c.config.getBool('stub-verbose', default=False)
                self.warn = c.config.getBool('stub-warn', default=False)
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
                """Return a list of *all* lines from an @data node, including comments."""
                c = self.c
                aList = c.config.getData(kind, strip_comments=False, strip_data=False)
                if not aList:
                    g.trace(f"warning: no @data {kind} node")
                return aList
            #@+node:ekr.20160213070235.4: *6* msf.scan_d
            def scan_d(self, kind):
                """Return a dict created from an @data node of the given kind."""
                c = self.c
                aList = c.config.getData(kind, strip_comments=True, strip_data=True)
                d = {}
                if aList is None:
                    g.trace(f"warning: no @data {kind} node")
                for s in aList or []:
                    name, value = s.split(':', 1)
                    d[name.strip()] = value.strip()
                return d
            #@+node:ekr.20160213070235.5: *6* msf.scan_patterns
            def scan_patterns(self, kind):
                """Parse the config section into a list of patterns, preserving order."""
                d = self.scan_d(kind)
                aList = []
                seen = set()
                for key in d:
                    value = d.get(key)
                    if key in seen:
                        g.trace('duplicate key', key)
                    else:
                        seen.add(key)
                        aList.append(self.msf.Pattern(key, value))
                return aList
            #@+node:ekr.20160213070235.6: *5* msf.finalize
            def finalize(self, fn):
                """Finalize and regularize a filename."""
                return g.os_path_normpath(g.os_path_abspath(g.os_path_expanduser(fn)))
            #@+node:ekr.20160213070235.7: *5* msf.make_stub_file
            def make_stub_file(self, p):
                """Make a stub file in ~/stubs for the @<file> node at p."""
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
                node = ast.parse(s, filename=fn, mode='exec')
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
                """Make stub files for all files in p's tree."""
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
        """
        Converts python text to coffeescript text. The conversion is not
        perfect, but it eliminates a lot of tedious text manipulation.
        """
        #@+others
        #@+node:ekr.20160316092837.1: *4* class Python_To_Coffeescript_Adapter
        class Python_To_Coffeescript_Adapter:
            """An interface class between Leo and leo/external/py2cs.py."""
            #@+others
            #@+node:ekr.20160316112717.1: *5* py2cs.ctor
            def __init__(self, c):
                """Ctor for Python_To_Coffeescript_Adapter class."""
                self.c = c
                self.files = []
                self.output_directory = self.finalize(
                    c.config.getString('py2cs-output-directory'))
                # self.output_fn = None
                self.overwrite = c.config.getBool('py2cs-overwrite', default=False)
                # Connect to the external module.
                self.py2cs = g.import_module('leo.external.py2cs')
            #@+node:ekr.20160316093019.1: *5* py2cs.main
            def main(self):
                """Main line for Python_To_CoffeeScript class."""
                if self.py2cs:
                    self.run()
                else:
                    g.es_print('can not load py2cs.py')
            #@+node:ekr.20160316094011.7: *5* py2cs.finalize
            def finalize(self, fn):
                """Finalize and regularize a filename."""
                return g.os_path_normpath(g.os_path_abspath(g.os_path_expanduser(fn)))
            #@+node:ekr.20160316094011.8: *5* py2cs.to_coffeescript
            def to_coffeescript(self, p):
                """Convert the @<file> node at p to a .coffee file."""
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
                """Create .coffee files for all @<file> nodes in p's tree."""
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
                """
                Strip s of all sentinel lines.
                This may be dubious because it destroys outline structure.
                """
                delims = ['#', None, None]
                return ''.join(
                    [z for z in g.splitLines(s) if not g.is_sentinel(z, delims)])
            #@-others
        #@-others
        c = self.c
        Python_To_Coffeescript_Adapter(c).main()
        c.bodyWantsFocus()
    #@+node:ekr.20211013080132.1: *3* ccc.python-to-typescript
    @cmd('python-to-typescript')
    def pythonToTypescriptCommand(self, event):
        """
        The python-to-typescript command converts python to typescript text.
        The conversion is not perfect, but it eliminates a lot of tedious text
        manipulation.
        """
        c = self.c
        self.PythonToTypescript(c).convert(c.p)
        self.c.bodyWantsFocus()
    #@+node:ekr.20211013080132.2: *4* class PythonToTypescript
    #@@nobeautify
    class PythonToTypescript:

        def __init__(self, c):
            self.c = c

        #@+others
        #@+node:ekr.20211013081549.1: *5* py2ts.convert
        def convert(self, p):
            """
            The main line.
            
            Convert p and all descendents as a child of a new last top-level node.
            """
            c = self.c
            # Create the parent node.
            parent = c.lastTopLevel().insertAfter()
            parent.h = p.h.replace('@', 'converted ')
            parent.b = '@language typescript\n'
            # Convert p, and recursively all nodes.
            self.convert_node(p, parent)
        #@+node:ekr.20211013102209.1: *5* py2ts.convert_body & helpers
        def convert_body(self, p, target):
            """
            Convert p.b into target.b.
            
            This is the heart of the algorithm.
            """
            patterns = (
                (self.comment_pat, self.do_comment),  # Should be first.
                (self.class_pat, self.do_class),
                (self.docstring_pat, self.do_docstring),
                (self.def_pat, self.do_def),
                (self.elif_pat, self.do_elif),
                (self.else_pat, self.do_else),
                (self.except_pat, self.do_except),
                (self.finally_pat, self.do_finally),
                (self.for_pat, self.do_for),
                (self.if_pat, self.do_if),
                (self.try_pat, self.do_try),
                (self.while_pat, self.do_while),
                (self.with_pat, self.do_with),
                (self.trailing_comment_pat, self.do_trailing_comment)  # Should be last.
            )
            # The loop may change lines, but each line is scanned only once.
            i, lines = 0, g.splitLines(p.b)
            old_lines = lines[:]
            while i < len(lines):
                progress = i
                line = lines[i]
                for (pattern, handler) in patterns:
                    m = pattern.match(line)
                    if m:
                        i = handler(i, lines, m, p) # May change lines.
                        break
                else:
                    i += 1
                assert progress < i
            if False and g.unitTesting and lines != old_lines:
                print(f"\nchanged {p.h}:\n")
                for z in lines:
                    print(z.rstrip())
            # Always set target.b!
            target.b = ''.join(lines).replace('@language python', '@language typescript')
            # Munge target.h.
            target.h = target.h.replace('__init__', 'constructor').replace('ctor', 'constructor')
        #@+node:ekr.20211014023141.1: *6* py2ts.do_class
        class_pat = re.compile(r'^([ \t]*)class(.*?):(.*?)\n')

        def do_class(self, i, lines, m, p):
            j = self.find_indented_block(i, lines, m, p)
            lws, base, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}class{base} {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1  # Rescan.
        #@+node:ekr.20211013165615.1: *6* py2ts.do_comment
        comment_pat = re.compile(r'^([ \t]*)#(.*?)\n')

        def do_comment(self, i, lines, m, p):
            """Handle a stand-alone comment line."""
            lws, comment = m.group(1), m.group(2).strip()
            lines[i] = f"{lws}/* {comment} */\n"
            return i + 1  # Advance.
        #@+node:ekr.20211013130041.1: *6* py2ts.do_def & helper
        def_pat = re.compile(r'^([ \t]*)def[ \t]+([\w_]+)\s*\((.*?)\):(.*?)\n')

        def do_def(self, i, lines, m, p):
            j = self.find_indented_block(i, lines, m, p)
            lws, name, args, tail = m.group(1), m.group(2), m.group(3).strip(), m.group(4).strip()
            args = self.do_args(args)
            if name == '__init__':
                name = 'constructor'
            tail_s = f" // {tail}" if tail else ''
            # Use void as a placeholder type.
            lines[i] = f"{lws}public {name} ({args}): void {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1  # Rescan.
        #@+node:ekr.20211014031722.1: *7* py2ts.do_args
        types_d = {
            # Use the typescript type conventions, not mypy conventions.
            'c': 'Commands',
            'gnx': 'string',
            'i': 'number',
            'j': 'number',
            'k': 'number',
            'p': 'Position',
            's': 'string',
            'v': 'VNode',
        }

        def do_args(self, args):
            result = []
            for arg in (z.strip() for z in args.split(',')):
                val = self.types_d.get(arg)
                result.append(f"{arg}: {val}" if val else arg)
            return ', '.join(result)
        #@+node:ekr.20211013165952.1: *6* py2ts.do_docstring
        docstring_pat = re.compile(r'^([ \t]*)("""|\'\'\')(.*?)\n')

        def do_docstring(self, i, lines, m, p):
            lws, delim, docstring = m.group(1), m.group(2), m.group(3).strip()
            tail = docstring.replace(delim,'').strip()
            if delim in docstring:
                lines[i] = f"{lws}/* {tail} */\n"
                return i + 1 # Advance.
            lines[i] = f"{lws}/** {tail}\n"
            i += 1
            while i < len(lines):
                line = lines[i]
                # Buglet: ignores whatever might follow.
                tail = line.replace(delim,'').strip()
                # pylint: disable=no-else-return
                if delim in line:
                    if tail:
                        lines[i] = f"{lws} * {tail}\n"
                        lines.insert(i + 1, f"{lws} */\n")
                        return i + 2  # Advance.
                    else:
                        lines[i] = f"{lws} */\n"
                        return i + 1  # Advance
                elif tail:
                    lines[i] = f"{lws} * {tail}\n"
                else:
                    lines[i] = f"{lws} *\n"
                i += 1
            return i
        #@+node:ekr.20211014030113.1: *6* py2ts.do_except
        except_pat = re.compile(r'^([ \t]*)except(.*?):(.*?)\n')

        def do_except(self, i, lines, m, p):
            j = self.find_indented_block(i, lines, m, p)
            lws, error, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
            tail_s = f" // {tail}" if tail else ''
            error_s = f" ({error}) " if error else ''
            lines[i] = f"{lws}except{error_s}{{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1  # Rescan.
        #@+node:ekr.20211013141725.1: *6* py2ts.do_for
        for_pat = re.compile(r'^([ \t]*)for[ \t]+(.*?):(.*?)\n')

        def do_for(self, i, lines, m, p):
            j = self.find_indented_block(i, lines, m, p)
            lws, cond, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}for ({cond}) {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1  # Rescan.
        #@+node:ekr.20211014022432.1: *6* py2ts.do_elif
        elif_pat = re.compile(r'^([ \t]*)elif[ \t]+(.*?):(.*?)\n')

        def do_elif(self, i, lines, m, p):
            indent = ' '*4
            j = self.find_indented_block(i, lines, m, p)
            lws, cond, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
            tail_s = f" // {tail}" if tail else ''
            line1 = f"{lws}else {{\n"
            line2 = f"{lws}{indent}if ({cond}) {{{tail_s}\n"
            lines[i] = line1 + line2
            tail1 = f"{indent}{lws}}}\n"
            tail2 = f"{lws}}}\n"
            lines.insert(j, tail1 + tail2)
            # Indent the indented block.
            for n in range(i + 1, j):
                lines[n] = indent + lines[n]
            return i + 1  # Rescan.
        #@+node:ekr.20211014022445.1: *6* py2ts.do_else
        else_pat = re.compile(r'^([ \t]*)else:(.*?)\n')

        def do_else(self, i, lines, m, p):
            j = self.find_indented_block(i, lines, m, p)
            lws, tail = m.group(1), m.group(2).strip()
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}else {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1  # Rescan.
        #@+node:ekr.20211014022453.1: *6* py2ts.do_finally
        finally_pat = re.compile(r'^([ \t]*)finally:(.*?)\n')

        def do_finally(self, i, lines, m, p):
            j = self.find_indented_block(i, lines, m, p)
            lws, tail = m.group(1), m.group(2).strip()
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}finally {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1  # Rescan.
        #@+node:ekr.20211013131016.1: *6* py2ts.do_if
        if_pat = re.compile(r'^([ \t]*)if[ \t]+(.*?):(.*?)\n')

        def do_if(self, i, lines, m, p):
            j = self.find_indented_block(i, lines, m, p)
            lws, cond, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}if ({cond}) {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1  # Rescan.
        #@+node:ekr.20211014022506.1: *6* py2ts.do_try
        try_pat = re.compile(r'^([ \t]*)try:(.*?)\n')

        def do_try(self, i, lines, m, p):
            j = self.find_indented_block(i, lines, m, p)
            lws, tail = m.group(1), m.group(2).strip()
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}try {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1  # Rescan.
        #@+node:ekr.20211013141809.1: *6* py2ts.do_while
        while_pat = re.compile(r'^([ \t]*)while[ \t]+(.*?):(.*?)\n')

        def do_while(self, i, lines, m, p):
            j = self.find_indented_block(i, lines, m, p)
            lws, cond, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
            tail_s = f" // {tail}" if tail else ''
            lines[i] = f"{lws}while ({cond}) {{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1  # Rescan.
        #@+node:ekr.20211014022554.1: *6* py2ts.do_with
        with_pat = re.compile(r'^([ \t]*)with(.*?):(.*?)\n')

        def do_with(self, i, lines, m, p):
            j = self.find_indented_block(i, lines, m, p)
            lws, clause, tail = m.group(1), m.group(2).strip(), m.group(3).strip()
            tail_s = f" // {tail}" if tail else ''
            clause_s = f" ({clause}) " if clause else ''
            lines[i] = f"{lws}with{clause_s}{{{tail_s}\n"
            lines.insert(j, f"{lws}}}\n")
            return i + 1  # Rescan.
        #@+node:ekr.20211013172540.1: *6* py2ts.do_trailing_comment
        trailing_comment_pat = re.compile(r'^([ \t]*)(.*?)#(.*?)\n')

        def do_trailing_comment(self, i, lines, m, p):
            """
            Handle a trailing comment line.
            
            All other patterns have already been scanned on the line.
            """
            lws, statement, trailing_comment = m.group(1), m.group(2).rstrip(), m.group(3).strip()
            lines[i] = f"{lws}{statement}  /* {trailing_comment} */\n"
            return i + 1  # Advance.
        #@+node:ekr.20211013123001.1: *6* py2ts.find_indented_block
        lws_pat = re.compile(r'^([ \t]*)')

        def find_indented_block(self, i, lines, m, p):
            """Return j, the index of the line *after* the indented block."""
            # Scan for the first non-empty line with the same or less indentation.
            lws = m.group(1)
            j = i + 1
            while j < len(lines):
                line = lines[j]
                m2 = self.lws_pat.match(line)
                lws2 = m2.group(1)
                if line.strip() and len(lws2) <= len(lws):
                    break
                j += 1
            return j

        #@+node:ekr.20211013101327.1: *5* py2ts.convert_node
        def convert_node(self, p, parent):
            # Create a copy of p as the last child of parent.
            target = parent.insertAsLastChild()
            target.h = p.h.replace('@', '')
            # Convert p.b int child.b
            self.convert_body(p, target)
            # Recursively create all descendants.
            for child in p.children():
                self.convert_node(child, target)
        #@-others
    #@+node:ekr.20160316091843.2: *3* ccc.typescript-to-py
    @cmd('typescript-to-py')
    def tsToPy(self, event):
        """
        The typescript-to-python command converts typescript text to python
        text. The conversion is not perfect, but it eliminates a lot of tedious
        text manipulation.
        """
        #@+others
        #@+node:ekr.20150514063305.176: *4* class TS_To_Python (To_Python)
        class TS_To_Python(To_Python):
            #@+others
            #@+node:ekr.20150514063305.177: *5* ctor (TS_To_Python)
            def __init__(self, c):
                """Ctor for TS_To_Python class."""
                super().__init__(c)
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
                self.replaceComments(aList)  # should follow all calls to safe_replace
                self.removeTrailingWs(aList)
                r(aList, '\t ', '\t')  # happens when deleting declarations.
            #@+node:ekr.20150514063305.179: *6* comment_scope_ids
            def comment_scope_ids(self, aList):
                """convert (public|private|export) aLine to aLine # (public|private|export)"""
                scope_ids = ('public', 'private', 'export',)
                i = 0
                if any(self.match_word(aList, i, z) for z in scope_ids):
                    i = self.handle_scope_keyword(aList, i)
                while i < len(aList):
                    progress = i
                    if self.is_string_or_comment(aList, i):
                        i = self.skip_string_or_comment(aList, i)
                    elif aList[i] == '\n':
                        i += 1
                        i = self.skip_ws(aList, i)
                        if any(self.match_word(aList, i, z) for z in scope_ids):
                            i = self.handle_scope_keyword(aList, i)
                    else:
                        i += 1
                    assert i > progress
                # print "handAllKeywords2:", ''.join(aList)
            #@+node:ekr.20150514063305.180: *7* handle_scope_keyword
            def handle_scope_keyword(self, aList, i):
                i1 = i
                # pylint: disable=undefined-loop-variable
                for word in ('public', 'private', 'export'):
                    if self.match_word(aList, i, word):
                        i += len(word)
                        break
                else:
                    return None
                # Skip any following spaces.
                i2 = self.skip_ws(aList, i)
                # Scan to the next newline:
                i3 = self.skip_line(aList, i)
                # Optional: move the word to a trailing comment.
                comment: List[str] = list(f" # {word}") if False else []
                # Change the list in place.
                aList[i1:i3] = aList[i2:i3] + comment
                i = i1 + (i3 - i2) + len(comment)
                return i
            #@+node:ekr.20150514063305.181: *6* handle_all_keywords
            def handle_all_keywords(self, aList):
                """
                converts if ( x ) to if x:
                converts while ( x ) to while x:
                """
                statements = ('elif', 'for', 'if', 'while',)
                i = 0
                while i < len(aList):
                    if self.is_string_or_comment(aList, i):
                        i = self.skip_string_or_comment(aList, i)
                    elif any(self.match_word(aList, i, z) for z in statements):
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
                    aList[i : i + 1] = [' ', c]
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
                    if i < j < len(aList):
                        ch = aList[j]
                        aList[j : j + 1] = [ch, ":", " "]
                        j = j + 2
                    return j
                return i
            #@+node:ekr.20150514063305.183: *6* mungeAllClasses
            def mungeAllClasses(self, aList):
                """Scan for a '{' at the top level that is preceeded by ')' """
                i = 0
                while i < len(aList):
                    progress = i
                    if self.is_string_or_comment(aList, i):
                        i = self.skip_string_or_comment(aList, i)
                    elif self.match_word(aList, i, 'class'):
                        i1 = i
                        i = self.skip_line(aList, i)
                        aList[i - 1 : i] = list(f"{aList[i - 1]}:")
                        s = ''.join(aList[i1:i])
                        k = s.find(' extends ')
                        if k > -1:
                            k1 = k
                            k = g.skip_id(s, k + 1)
                            k = g.skip_ws(s, k)
                            if k < len(s) and g.is_c_id(s[k]):
                                k2 = g.skip_id(s, k)
                                word = s[k:k2]
                                aList[i1:i] = list(f"{s[:k1]} ({word})")
                    elif self.match_word(aList, i, 'interface'):
                        aList[i : i + len('interface')] = list('class')
                        i = self.skip_line(aList, i)
                        aList[i - 1 : i] = list(f"{aList[i - 1]}: # interface")
                        i = self.skip_line(aList, i)  # Essential.
                    else:
                        i += 1
                    assert i > progress
            #@+node:ekr.20150514063305.184: *6* mungeAllFunctions & helpers
            def mungeAllFunctions(self, aList):
                """Scan for a '{' at the top level that is preceeded by ')' """
                prevSemi = 0  # Previous semicolon: header contains all previous text
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
                        j = self.handlePossibleFunctionHeader(
                            aList, i, prevSemi, firstOpen)
                        prevSemi = j
                        firstOpen = None  # restart the scan
                    else:
                        j = i + 1
                    # Handle unusual cases.
                    if j <= progress:
                        j = progress + 1
                    assert j > progress
                    i = j
            #@+node:ekr.20150514063305.185: *7* handlePossibleFunctionHeader
            def handlePossibleFunctionHeader(self, aList, i, prevSemi, firstOpen):
                """
                converts function header lines from typescript format to python format.
                That is, converts
                    x1..nn w::y ( t1 z1,..tn zn) { C++
                    (public|private|export) name (t1: z1, ... tn: zn {
                to
                    def y (z1,..zn): { # (public|private|export)
                """
                assert self.match(aList, i, "{")
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
                assert aList[open_paren] == '('
                head = aList[prevSemi:open_paren]
                # do nothing if the head starts with "if", "for" or "while"
                k = self.skip_ws(head, 0)
                if k >= len(head) or not head[k].isalpha():
                    return 1 + self.skip_to_matching_bracket(aList, i)
                kk = self.skip_past_word(head, k)
                if kk > k:
                    headString = ''.join(head[k:kk])
                    # C keywords that might be followed by '{'
                    # print "headString:", headString
                    if headString in ["do", "for", "if", "struct", "switch", "while"]:
                        return 1 + self.skip_to_matching_bracket(aList, i)
                args = aList[open_paren : close + 1]
                k = 1 + self.skip_to_matching_bracket(aList, i)
                body = aList[close + 1 : k]
                head = self.massageFunctionHead(head)
                args = self.massageFunctionArgs(args)
                body = self.massageFunctionBody(body)
                result = []
                if head:
                    result.extend(head)
                if args:
                    result.extend(args)
                if body:
                    result.extend(body)
                aList[prevSemi:k] = result
                return prevSemi + len(result)
            #@+node:ekr.20150514063305.186: *7* massageFunctionArgs
            def massageFunctionArgs(self, args):
                assert args[0] == '('
                assert args[-1] == ')'
                result = ['(']
                lastWord = []
                if self.class_name:
                    for item in list("self,"):
                        result.append(item)  #can put extra comma
                i = 1
                while i < len(args):
                    i = self.skip_ws_and_nl(args, i)
                    ch = args[i]
                    if ch.isalpha():
                        j = self.skip_past_word(args, i)
                        lastWord = args[i:j]
                        i = j
                    elif ch == ',' or ch == ')':
                        for item in lastWord:
                            result.append(item)
                        if lastWord != [] and ch == ',':
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
                result: List[Any] = []
                prevWord = []
                self.class_name = ''
                i = 0
                while i < len(head):
                    i = self.skip_ws_and_nl(head, i)
                    if i < len(head) and head[i].isalpha():
                        result = []
                        j = self.skip_past_word(head, i)
                        prevWord = head[i:j]
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
                                if head[i:j] == prevWord:
                                    result.extend('__init__')
                                elif head[i] == '~' and head[i + 1 : j] == prevWord:
                                    result.extend('__del__')
                                else:
                                    # result.extend(list('::'))
                                    result.extend(head[i:j])
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
                """
                Look for '{' preceded by '{' or '}' or ';'
                (with intervening whitespace and comments).
                """
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
                            if k == j:
                                break
                            assert k < j
                        if self.match(body, j, '{'):
                            k = j
                            j = self.skip_to_matching_bracket(body, j)
                            m = '# <Start dedented block>...'
                            body[k : k + 1] = list(m)
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
                                        del body[k - spaces : k]
                                        k -= spaces
                                        j -= spaces
                                else:
                                    k += 1
                                assert progress < k
                            m = '    # <End dedented block>'
                            body[j : j + 1] = list(m)
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
        TS_To_Python(c).go()
        c.bodyWantsFocus()
    #@+node:ekr.20160321042444.1: *3* ccc.import-jupyter-notebook
    @cmd('import-jupyter-notebook')
    def importJupyterNotebook(self, event):
        """Prompt for a Jupyter (.ipynb) file and convert it to a Leo outline."""
        try:
            import nbformat
            assert nbformat
        except ImportError:
            g.es_print('import-jupyter-notebook requires nbformat package')
            return
        from leo.plugins.importers.ipynb import Import_IPYNB
        # was @-others
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
        """Convert the present outline to a .ipynb file."""
        from leo.plugins.writers.ipynb import Export_IPYNB
        c = self.c
        Export_IPYNB(c).export_outline(c.p)
    #@-others
#@+node:ekr.20210902013852.1: ** Converter classes for @test
# Classes to convert @test nodes to proper unit tests.
#@+node:ekr.20201202083003.1: *3* class ConvertAtTests
class ConvertAtTests:
    """
    A class that converts @test nodes to proper unit tests.

    Subclasses specialize the convert method.

    These scripts know nothing about the unit tests they create. They just
    pass the data from the old tests to the new tests using args in the
    run_test method.
    """

    class_name = "TestXXX"  # Later, change headlines with search/replace!

    #@+others
    #@+node:ekr.20201130075024.2: *4* ConvertAtTests.body
    def body(self, after_p, after_sel, before_p, before_sel, command_name):
        """Return the body of the test"""
        real_command_name = command_name.split(' ')[0]
        sel11, sel12 = before_sel.split(',')
        sel21, sel22 = after_sel.split(',')
        delim = "'''" if '"""' in before_p.b else '"""'
        return (
            f"def test_{self.function_name(command_name)}(self):\n"
            f'    """Test case for {command_name}"""\n'
            f'    c = self.c\n'
            f'    before_b = {delim}\\\n'
            f"{before_p.b}"
            f'{delim}\n'
            f'    after_b = {delim}\\\n'
            f"{after_p.b}"
            f'{delim}\n'
            f"    self.run_test(\n"
            f"        before_b=before_b,\n"
            f"        after_b=after_b,\n"
            f'        before_sel=("{sel11}", "{sel12}"),\n'
            f'        after_sel=("{sel21}", "{sel22}"),\n'
            f'        command_name="{real_command_name}",\n'
            f"    )\n"
        )
    #@+node:ekr.20210829142807.1: *4* ConvertAtTests.clean_headline
    def clean_headline(self, p):
        """Make p.h suitable as a function.name."""
        h = p.h
        if h.startswith('@test'):
            h = h[len('@test') :]
        h = h.strip()
        result = []
        for ch in h:
            if ch.isalnum():
                result.append(ch)
            else:
                result.append('_')
        return ''.join(result).replace('__', '_')
    #@+node:ekr.20210902014405.1: *4* ConvertAtTests.convert_nodes
    def convert_nodes(self, c, root):
        """
        Use converter.convert() to convert all the @test nodes in the
        root's tree to children a new last top-level node.
        """
        if not root:
            print('no root')
            return
        last = c.lastTopLevel()
        target = last.insertAfter()
        target.h = 'Converted nodes'
        count = 0
        for p in root.subtree():
            if p.h.startswith('@test'):
                self.convert_node(c, p, target)
                count += 1
        target.expand()
        c.redraw(target)
        print(f"converted {count} @test nodes")
    #@+node:ekr.20210829142231.2: *4* ConvertAtTests.convert_node
    def convert_node(self, c, p, target):
        """
        Convert p, an @test node, creating a new node as the last child of
        target.

        May be overridden in subclasses.
        """
        # Calculate the headline and body text.
        test_name = f"test_{self.clean_headline(p)}"
        body = textwrap.indent(p.b, ' ' * 4).rstrip()
        # Create the new node.
        test_node = target.insertAsLastChild()
        test_node.h = f"{self.class_name}.{test_name}"
        test_node.b = f"def {test_name}(self):\n    c = self.c\n{body}\n"
    #@+node:ekr.20210907154923.1: *4* ConvertAtTests.copy_children
    def copy_children(self, c, p, target):
        """Copy all children of p to the target."""
        for child in p.children():
            target2 = target.insertAsLastChild()
            target2.h = child.h
            target2.b = child.b
            self.copy_children(c, child, target2)
    #@+node:ekr.20201130075024.5: *4* ConvertAtTests.function_name
    def function_name(self, command_name):
        """Convert a command name into a test function."""
        result = []
        parts = command_name.split('-')
        for part in parts:
            s = part.replace('(', '').replace(')', '')
            inner_parts = s.split(' ')
            result.append('_'.join(inner_parts))
        return '_'.join(result)
    #@-others
#@+node:ekr.20210905151425.1: *3* class ConvertColorizerTests (ConvertAtTests)
class ConvertColorizerTests(ConvertAtTests):
    """Convert @test nodes for colorizer commands."""
    #@+others
    #@+node:ekr.20210905151425.2: *4* ConvertColorizerTests.convert_node
    def convert_node(self, c, p, target):
        """Convert one @test node, creating a new node."""
        indent = ' ' * 4
        # Create the new node.
        test_node = target.insertAsLastChild()
        # Set the headline.
        test_name = f"test_{self.clean_headline(p)}"
        test_node.h = f"{self.class_name}.{test_name}"
        # Compute the start of the body text.
        result = [
            f"def {test_name}(self):\n",
            f"{indent}c = self.c\n",
        ]
        # Compute the data, if there is a child node.
        child = p.firstChild()
        if child:
            child_s = child.b.rstrip()
            pat = re.compile(r'@language (\w+)\s*\n')
            m = pat.search(child.b)
            if m:
                # g.trace(child.h, m.group(0).rstrip())
                child_s = child_s.replace(m.group(0), '')
                language_name = m.group(1)
                result.append(f'''{indent}text = textwrap.dedent("""\\\n''')
                result.append(child_s.rstrip() + '\n')
                result.append('''""")\n''')
                result.append(f"{indent}self.color('{language_name}', text)\n")
                test_node.b = ''.join(result)
                # result.append(f"{indent}language_name = '{m.group(1)}'\n")
                return
        # Default:
        # Compute the tail.
        body = textwrap.indent(p.b, ' ' * 4).rstrip()
        result.append(f"{body}\n")
        # Set the body text!
        test_node.b = ''.join(result)
    #@-others
#@+node:ekr.20201202083553.1: *3* class ConvertEditCommandsTests (ConvertAtTests)
class ConvertEditCommandsTests(ConvertAtTests):
    """Convert @edit nodes for edit commands."""
    #@+others
    #@+node:ekr.20201130075024.4: *4* ConvertEditCommandsTests.convert_node
    def convert_node(self, c, p, target):
        """Convert one @test node, creating a new node."""
        after_p, before_p = None, None
        after_sel, before_sel = None, None
        assert p.h.startswith('@test')
        command_name = p.h[len('@test') :].strip()
        for child in p.children():
            if child.h.startswith('after'):
                after_p = child.copy()
                after_sel = child.h[len('after') :].strip()
                after_sel = after_sel.replace('sel=', '').strip()
            elif child.h.startswith('before'):
                before_p = child.copy()
                before_sel = child.h[len('before') :].strip()
                before_sel = before_sel.replace('sel=', '').strip()
        assert before_p and after_p
        assert before_sel and after_sel
        new_child = target.insertAsLastChild()
        new_child.h = command_name
        new_child.b = self.body(after_p, after_sel, before_p, before_sel, command_name)
    #@-others
#@+node:ekr.20210908062600.1: *3* class ConvertShadowTests (ConvertAtTests)
class ConvertShadowTests(ConvertAtTests):
    """Convert @test nodes for @shadow commands."""
    #@+others
    #@+node:ekr.20210908062651.1: *4* ConvertShadowTests.convert_node
    def convert_node(self, c, p, target):
        """Convert one @test node, creating a new node."""
        assert p.h.startswith('@test')
        old_p = g.findNodeInChildren(c, p, 'old')
        assert old_p, p.h
        new_p = g.findNodeInChildren(c, p, 'new')
        assert new_p, p.h
        # Create the new node and init the headline.
        indent = ' ' * 4
        test_node = target.insertAsLastChild()
        test_name = f"test_{self.clean_headline(p)}"
        test_node.h = f"{self.class_name}.{test_name}"
        # Calculate old_s.
        old_list = []
        for z in g.splitLines(old_p.b.rstrip()):
            old_list.append(f"{indent}{indent}{z.rstrip()}\n")
        for child in old_p.children():
            for z in g.splitLines(child.b.rstrip()):
                old_list.append(f"{indent}{indent}{z.rstrip()}\n")
        old_s = ''.join(old_list)
        # Calculate new_s.
        new_list = []
        for z in g.splitLines(new_p.b.rstrip()):
            new_list.append(f"{indent}{indent}{z.rstrip()}\n")
        for child in new_p.children():
            for z in g.splitLines(child.b.rstrip()):
                new_list.append(f"{indent}{indent}{z.rstrip()}\n")
        new_s = ''.join(new_list)
        # Set the body text!
        test_node.b = ''.join([
            # The start of the test.
            f"def {test_name}(self):\n",
            f"{indent}p = self.c.p\n",
            # Create the 'old' node.
            f"{indent}# Create the 'old' node.\n"
            f"{indent}old = p.insertAsLastChild()\n",
            f"{indent}old.h = 'old'\n",
            f"{indent}old.b = textwrap.dedent(\"\"\"\\\n",
            old_s,
            f"{indent}\"\"\")\n",
            # Create the 'new' node.
            f"{indent}# Create the 'new' node.\n"
            f"{indent}new = p.insertAsLastChild()\n",
            f"{indent}new.h = 'new'\n",
            f"{indent}new.b = textwrap.dedent(\"\"\"\\\n",
            new_s,
            f"{indent}\"\"\")\n",
            # The test.
            f"{indent}# Run the test.\n",
            f"{indent}results, expected = self.make_lines(old, new)\n",
            f"{indent}self.assertEqual(results, expected)\n",
        ])
    #@-others
#@+node:ekr.20210906140154.1: *3* class ConvertUndoTests (ConvertAtTests)
class ConvertUndoTests(ConvertAtTests):
    """Convert @test nodes for undo commands."""
    #@+others
    #@+node:ekr.20210906140220.1: *4* ConvertUndoTests.convert_node
    def convert_node(self, c, p, target):
        """Convert one @test node, creating a new node."""
        assert p.h.startswith('@test')
        before = g.findNodeInTree(c, p, 'before')
        after = g.findNodeInTree(c, p, 'after')
        sel = g.findNodeInTree(c, p, 'selection')
        # Do regular conversion if the nodes don't come from the children of @suite.
        if not (before and after and sel):
            super().convert_node(c, p, target)
            return
        # Create the new node.
        indent = ' ' * 4
        test_node = target.insertAsLastChild()
        # Set the headline.
        test_name = f"test_{self.clean_headline(p)}"
        test_node.h = f"{self.class_name}.{test_name}"
        # Compute the start of the body text.
        result = [
            f"def {test_name}(self):\n",
            f"{indent}c = self.c\n",
        ]
        # Append the assignment to 'before'.
        result.append(f'{indent}before = textwrap.dedent("""\\\n')
        for z in g.splitLines(before.b):
            result.append(f"{indent}{indent}{z.rstrip()}\n")
        result.append('""")\n')
        # Append the assignment to 'after'.
        result.append(f'{indent}after = textwrap.dedent("""\\\n')
        for z in g.splitLines(after.b):
            result.append(f"{indent}{indent}{z.rstrip()}\n")
        result.append('""")\n')
        # Compute the i, j values..
        lines = g.splitLines(sel.b)
        assert len(lines) >= 2
        row1, col1 = lines[0].split('.')
        row2, col2 = lines[1].split('.')
        i = g.convertRowColToPythonIndex(before.b, int(row1), int(col1))
        j = g.convertRowColToPythonIndex(before.b, int(row2), int(col2))
        # Compute the function name.
        pat = re.compile(r'@test (\w+)')
        m = pat.match(p.h)
        func = m.group(1)
        # Compute the tail.
        result.append(f"{indent}i, j = {i}, {j}\n")
        result.append(f"{indent}func = c.{func}\n")  # Changed
        result.append(f"{indent}self.runTest(before, after, i, j, func)\n")
        # Set the body text!
        test_node.b = ''.join(result)
    #@-others
#@-others
#@-leo
