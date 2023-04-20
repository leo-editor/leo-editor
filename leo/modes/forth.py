#@+leo-ver=5-thin
#@+node:ekr.20150326145530.1: * @file ../modes/forth.py
# Hand-written Leo colorizer control file for forth mode.
# This file is in the public domain.
#@@killbeautify
from leo.core import leoGlobals as g
#@+<< define mode rules >>
#@+node:ekr.20150326145530.2: ** << define mode rules >> (forth.py)
# Rules for forth_main ruleset.

def forth_block_comment_rule(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="(", end=")",
        at_word_start=True)

def forth_comment_rule(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="\\",
        at_word_start=True)

def forth_keyword_rule(colorer, s, i):
    return colorer.match_keywords(s, i)

def forth_string_rule(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_word_start=True)

# ==========================

if 0:

    def forth_rule0(colorer, s, i):
        return colorer.match_eol_span(s, i, kind="comment1", seq="#")

    def forth_rule1(colorer, s, i):
        return colorer.match_span(s, i, kind="literal2", begin="\"\"\"", end="\"\"\"")

    def forth_rule2(colorer, s, i):
        return colorer.match_span(s, i, kind="literal2", begin="'''", end="'''")

    def forth_rule3(colorer, s, i):
        return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

    def forth_rule4(colorer, s, i):
        return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

    def forth_rule5(colorer, s, i):
        return colorer.match_plain_seq(s, i, kind="operator", seq="=")

    def forth_rule6(colorer, s, i):
        return colorer.match_plain_seq(s, i, kind="operator", seq="!")

    def forth_rule7(colorer, s, i):
        return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

    def forth_rule8(colorer, s, i):
        return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

    def forth_rule9(colorer, s, i):
        return colorer.match_plain_seq(s, i, kind="operator", seq="+")

    def forth_rule10(colorer, s, i):
        return colorer.match_plain_seq(s, i, kind="operator", seq="-")

    def forth_rule11(colorer, s, i):
        return colorer.match_plain_seq(s, i, kind="operator", seq="/")

    def forth_rule12(colorer, s, i):
        return colorer.match_plain_seq(s, i, kind="operator", seq="*")

    def forth_rule13(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq=">")

    def forth_rule14(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="<")

    def forth_rule15(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="%")

    def forth_rule16(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="&")

    def forth_rule17(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="|")

    def forth_rule18(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="^")

    def forth_rule19(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="~")

    # #1821.
    def forth_rule20(colorer, s, i):
        return 0

    def forth_rule21(colorer, s, i):
        return colorer.match_keywords(s, i)
#@-<< define mode rules >>
#@+<< define mode data >>
#@+node:ekr.20150326145530.3: ** << define mode data >> (forth.py)
# Properties for forth mode.

properties = {
    # "indentNextLines": "\\s*[^#]{3,}:\\s*(#.*)?",
    "lineComment": "\\",
}
# Attributes dict for forth_main ruleset.
forth_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    # "escape": "\\",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": "",
}
# Dictionary of attributes dictionaries for forth mode.
attributesDictDict = {
    "forth_main": forth_main_attributes_dict,
}
# Keywords dict for forth_main ruleset.
forth_main_keywords_dict = {}  # Created by extendForth class.
# Dictionary of keywords dictionaries for forth mode.
keywordsDictDict = {
    "forth_main": forth_main_keywords_dict,
}
# Rules dict for forth_main ruleset.
# This is extended by extendForth.
rulesDict = {
    '(': [forth_block_comment_rule],
    '\\': [forth_comment_rule],
    '"': [forth_string_rule],
}
# x.rulesDictDict for forth mode.
rulesDictDict = {
    "forth_main": rulesDict,
}
# Import dict for forth mode.
importDict = {}
#@-<< define mode data >>
#@+<< define extendForth class >>
#@+node:ekr.20150326145530.4: ** << define extendForth class >> (forth.py)
class extendForth:
    """A helper class to extend the mode tables from @data forth-x settings."""

    #@+others
    #@+node:ekr.20150326145530.5: *3* ctor
    def __init__(self):
        self.c = None  # set by pre_init_mode function.
        #
        # Default forth keywords: extended by @data forth-words
        # Forth words to be rendered in boldface: extended by @data forth-bold-words
        self.boldwords = []
        #
        # Forth bold-italics words: extended by @data forth-bold-italic-words
        # Note: on some boxen, bold italics may show in plain bold.
        self.bolditalicwords = []
        #
        # Forth words that define brackets: extended by @data forth-delimiter-pairs
        self.brackets = []  # Helper: a list of tuples.
        self.brackets1 = []
        self.brackets2 = []
        #
        # Words which define other words: extended by forth-defwords
        self.definingwords = []
        #
        # Forth words to be rendered in italics: extended by forth-italic-words
        self.italicwords = []
        #
        # Default keywords: extended by @data forth-keywords
        self.keywords = []
            # "variable", "constant", "code", "end-code",
            # "dup", "2dup", "swap", "2swap", "drop", "2drop",
            # "r>", ">r", "2r>", "2>r",
            # "if", "else", "then",
            # "begin", "again", "until", "while", "repeat",
            # "v-for", "v-next", "exit",
            # "meta", "host", "target", "picasm", "macro",
            # "needs", "include",
            # "'", "[']",
            # # ":", # Now a defining word.
            # ";",
            # "@", "!", ",", "1+", "+", "-",
            # "<", "<=", "=", ">=", ">",
            # "invert", "and", "or",
        #
        # Forth words which start strings: extended by @data forth-string-word-pairs
        self.stringwords = []
        self.stringwords1 = []
        self.stringwords2 = []
        self.verbose = False  # True: tell when extending forth words.

    #@+node:ekr.20150326145530.6: *3* init & helper
    def init(self):
        """Set our ivars from settings."""
        c = self.c
        assert c
        table = (
            (self.definingwords, "forth-defwords"),
            (self.brackets, "forth-delimiter-pairs"),
            (self.keywords, "forth-words"),
            (self.stringwords, "forth-string-word-pairs"),
            (self.boldwords, "forth-bold-words"),
            (self.bolditalicwords, "forth-bold-italic-words"),
            (self.italicwords, "forth-italic-words"),
        )
        # Add entries from @data nodes (if they exist) to the corresponding lists.
        for (ivarList, setting) in table:
            extras = []
            aList = c.config.getData(setting)
            if aList:
                for s in aList:
                    s = s.strip()
                    if s and s[0] != '\\':
                        extras.append(s)
                if extras:
                    if self.verbose:
                        if not g.unitTesting and not g.app.batchMode:
                            g.pr("Found extra forth: %s" % " ".join(extras))
                    ivarList.extend(extras)
        # Create brackets1/2 and stringwords1/2 lists.
        table2 = (
            ("brackets", "@data forth-delimiter-pairs"),
            ("stringwords", "@data forth-string-word-pairs"),
        )
        for (ivar, setting) in table2:
            self.splitList(ivar, setting)

    #@+node:ekr.20150326145530.7: *4* splitList
    def splitList(self, ivar, setting):
        """Process lines containing pairs of entries
        in a list whose *name* is ivar.
        Put the results in ivars whose names are ivar1 and ivar2."""
        result1, result2 = [], []
        aList = getattr(self, ivar)
        # Look for pairs.  Comments have already been removed.
        for s in aList:
            pair = s.split(' ')
            if len(pair) == 2 and pair[0].strip() and pair[1].strip():
                result1.append(pair[0].strip())
                result2.append(pair[1].strip())
            else:
                g.es_print('%s: ignoring line: %s' % (setting, s))
        # Set the ivars.
        name1 = '%s1' % ivar
        name2 = '%s2' % ivar
        setattr(self, name1, result1)
        setattr(self, name2, result2)

    #@+node:ekr.20150326145530.8: *3* createBracketRules & helper
    def createBracketRules(self):
        for z in self.brackets1:
            func = self.createBracketRule(z)
            self.extendRulesDict(ch=z[0], func=func)

    def createBracketRule(self, begin):
        i = self.brackets1.index(begin)
        end = self.brackets2[i]

        def forth_bracket_rule(colorer, s, i):
            return colorer.match_span(s, i, kind="bracketRange", begin=begin, end=end,
                at_word_start=True, no_word_break=True)

        return forth_bracket_rule

    #@+node:ekr.20150326145530.9: *3* createDefiningWordRules & helper
    def createDefiningWordRules(self):
        for z in self.definingwords:
            func = self.createDefiningWordRule(z)
            self.extendRulesDict(ch=z[0], func=func)

    def createDefiningWordRule(self, word):

        def forth_defining_word_rule(colorer, s, i):

            return colorer.match_word_and_regexp(s, i,
                kind1="keyword2",  # defining word
                word=word,
                kind2="keyword3",  # bold
                pattern=r'(\s)*(\S)+')

        return forth_defining_word_rule

    #@+node:ekr.20150326145530.10: *3* createKeywords
    def createKeywords(self):
        """
        Create the mode keyword table and
        entries in the rulesDict for the forth_keyword_rule.
        """
        # global forth_main_keywords_dict
        # global forth_keyword_rule
        table = (
            (self.keywords, 'keyword1'),
          # (self.definingwords,    'keyword2'), # Done in createDefiningWordRules.
            (self.boldwords, 'keyword3'),
            (self.bolditalicwords, 'keyword4'),
            (self.italicwords, 'keyword5'),
            (self.stringwords, 'string'),
        )
        d = forth_main_keywords_dict
        for keywordList, kind in table:
            for z in keywordList:
                # Create the entry in the keyword table.
                if kind == 'string':
                    func = self.createStringRule(d, z)
                else:
                    func = forth_keyword_rule
                # Always make the entry.
                d[z] = kind
                self.extendRulesDict(ch=z[0], func=func)

    #@+node:ekr.20150326145530.11: *3* createStringRule
    def createStringRule(self, d, pair):
        """Create an entry in d for a string keyword."""
        aList = pair.split(' ')
        if len(aList) != 2:
            g.trace('can not happen: expecting pair of forth strings:', pair)
            return None
        begin, end = aList

        def forth_string_word_rule(colorer, s, i):
            return colorer.match_span(s, i, kind="literal1", begin=begin.strip(), end=end.strip(),
                at_word_start=True)

        return forth_string_word_rule

    #@+node:ekr.20150326145530.12: *3* extendRulesDict
    def extendRulesDict(self, ch, func):
        global rulesDict
        # Extend the rulesDict entry for the first character of z.
        aList = rulesDict.get(ch, [])
        if func not in aList:
            aList.append(func)
            rulesDict[ch] = aList

    #@-others
#@-<< define extendForth class >>
e = extendForth()

def pre_init_mode(c):
    e.c = c
    e.init()
    e.createKeywords()
    e.createBracketRules()
    e.createDefiningWordRules()

#@-leo
