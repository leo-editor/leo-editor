#@+leo-ver=4-thin
#@+node:ekr.20080703111151.1:@thin ../modes/forth.py
# Hand-written Leo colorizer control file for forth mode.
# This file is in the public domain.

import leo.core.leoGlobals as g

#@<< define mode rules >>
#@+node:ekr.20080703111151.8:<< define mode rules >>
# Rules for forth_main ruleset.

def forth_block_comment_rule(colorer, s, i):
        return colorer.match_span(s, i, kind="comment2", begin="(", end=")",
            at_line_start=False, at_whitespace_end=False, at_word_start=False,
            delegate="",exclude_match=False,
            no_escape=False, no_line_break=False, no_word_break=False)

def forth_comment_rule(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="\\",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def forth_keyword_rule(colorer, s, i):
    return colorer.match_keywords(s, i)

def forth_string_rule(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

# ==========================
if 0:

    def forth_rule0(colorer, s, i):
        return colorer.match_eol_span(s, i, kind="comment1", seq="#",
            at_line_start=False, at_whitespace_end=False, at_word_start=False,
            delegate="", exclude_match=False)

    def forth_rule1(colorer, s, i):
        return colorer.match_span(s, i, kind="literal2", begin="\"\"\"", end="\"\"\"",
            at_line_start=False, at_whitespace_end=False, at_word_start=False,
            delegate="",exclude_match=False,
            no_escape=False, no_line_break=False, no_word_break=False)

    def forth_rule2(colorer, s, i):
        return colorer.match_span(s, i, kind="literal2", begin="'''", end="'''",
            at_line_start=False, at_whitespace_end=False, at_word_start=False,
            delegate="",exclude_match=False,
            no_escape=False, no_line_break=False, no_word_break=False)

    def forth_rule3(colorer, s, i):
        return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
            at_line_start=False, at_whitespace_end=False, at_word_start=False,
            delegate="",exclude_match=False,
            no_escape=False, no_line_break=False, no_word_break=False)

    def forth_rule4(colorer, s, i):
        return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
            at_line_start=False, at_whitespace_end=False, at_word_start=False,
            delegate="",exclude_match=False,
            no_escape=False, no_line_break=False, no_word_break=False)

    def forth_rule5(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="=",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule6(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="!",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule7(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq=">=",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule8(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="<=",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule9(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="+",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule10(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="-",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule11(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="/",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule12(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="*",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule13(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq=">",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule14(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="<",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule15(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="%",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule16(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="&",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule17(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="|",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule18(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="^",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule19(colorer, s, i):
        return colorer.match_seq(s, i, kind="operator", seq="~",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

    def forth_rule20(colorer, s, i):
        return colorer.match_mark_previous(s, i, kind="function", pattern="(",
            at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=True)

    def forth_rule21(colorer, s, i):
        return colorer.match_keywords(s, i)
#@-node:ekr.20080703111151.8:<< define mode rules >>
#@nl
#@<< define mode data >>
#@+node:ekr.20080703111151.2:<< define mode data >>

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
forth_main_keywords_dict = {} # Created by extendForth class.

# Dictionary of keywords dictionaries for forth mode.
keywordsDictDict = {
	"forth_main": forth_main_keywords_dict,
}

# Rules dict for forth_main ruleset.
# This is extended by extendForth.
rulesDict = {
    '(':    [forth_block_comment_rule],
    '\\':   [forth_comment_rule],
    '"':    [forth_string_rule],
}

# x.rulesDictDict for forth mode.
rulesDictDict = {
    "forth_main": rulesDict,
}

# Import dict for forth mode.
importDict = {}

#@-node:ekr.20080703111151.2:<< define mode data >>
#@nl
#@<< define extendForth class >>
#@+node:ekr.20080703111151.4:<< define extendForth class >>
class extendForth:

    '''A helper class to extend the mode tables from plugins/leo-forthXXX.txt files.'''

    #@    @+others
    #@+node:ekr.20080703111151.5:ctor
    def __init__ (self):

        # Default forth keywords: extended by leo-forthwords.txt.

        # Forth words to be rendered in boldface: extended by leo-forthboldwords.txt.
        self.boldwords = [ ]

        # Forth bold-italics words: extemded leo-forthbolditalicwords.txt if present
        # Note: on some boxen, bold italics may show in plain bold.
        self.bolditalicwords = [ ]

        # Forth words that define brackets: extended by leo-forthdelimiters.txt
        self.brackets = []  # Helper: a list of tuples.
        self.brackets1 = []
        self.brackets2 = []

        # Words which define other words: extended by leo-forthdefwords.txt.
        self.definingwords = [
            ":", "variable", "constant", "code",
        ]

        # Forth words to be rendered in italics: extended by leo-forthitalicwords.txt.
        self.italicwords = [ ]

        # Default keywords.
        self.keywords = [
            "variable", "constant", "code", "end-code",
            "dup", "2dup", "swap", "2swap", "drop", "2drop",
            "r>", ">r", "2r>", "2>r",
            "if", "else", "then",
            "begin", "again", "until", "while", "repeat",
            "v-for", "v-next", "exit",
            "meta", "host", "target", "picasm", "macro",
            "needs", "include",
            "'", "[']",
            # ":", # Now a defining word.
            ";",
            "@", "!", ",", "1+", "+", "-",
            "<", "<=", "=", ">=", ">",
            "invert", "and", "or", 
            ]

        # Forth words which start strings: extended by leo-forthstringwords.txt.
        self.stringwords = [
            's"', '."', '"', '."',
            'abort"',
            ]

        self.verbose = False # True: tell when extending forth words.

        self.init()
        self.createKeywords()
        self.createBracketRules()
        self.createDefiningWordRules()
        # g.trace('rulesDict...\n',g.dictToString(rulesDict),tag='rulesDict...')
    #@-node:ekr.20080703111151.5:ctor
    #@+node:ekr.20080703111151.3:init
    def init (self):

        '''Set our ivars from external files.'''

        table = (
            (self.definingwords, "leo-forthdefwords.txt", "defining words"),
            (self.brackets, "leo-forthdelimiters.txt", "extra delimiter pairs"),
            (self.keywords, "leo-forthwords.txt", "words"),
            (self.stringwords, "leo-forthstringwords.txt", "string words"),
            (self.boldwords, "leo-forthboldwords.txt", "bold words"),
            (self.bolditalicwords, "leo-forthbolditalicwords.txt", "bold-italic words"),
            (self.italicwords, "leo-forthitalicwords.txt", "italic words"),
        )

        # Add entries from files (if they exist) to the corresponding lists.
        for (lst, path, typ) in table:
            try:
                extras = []
                path = g.os_path_join(g.app.loadDir,"..","plugins",path)
                for line in file(path).read().strip().split("\n"):
                    line = line.strip()
                    if line and line[0] != '\\':
                        extras.append(line)
                if extras:
                    if self.verbose: # I find this annoying.  YMMV.
                        if not g.app.unitTesting and not g.app.batchMode:
                            print "Found extra forth %s" % typ + ": " + " ".join(extras)
                    lst.extend(extras)
            except IOError:
                pass # print "Not found",path

        # Pair up entries in brackets list.
        self.brackets1 = [] ; self.brackets2 = []
        if self.brackets:
            if (len(self.brackets) % 2) == 1:
                g.es_print('leo-forthdelimiters.txt contain an odd number of entries',color='red')
            else:
                i = 0
                while i < len(self.brackets):
                    self.brackets1.append(self.brackets[i])
                    self.brackets2.append(self.brackets[i+1])
                    i += 2
                # g.trace('brackets1:',self.brackets1,'brackets2',self.brackets2)
    #@-node:ekr.20080703111151.3:init
    #@+node:ekr.20080703111151.9:createBracketRules & helper
    def createBracketRules (self):

        for z in self.brackets1:
            func = self.createBracketRule(z)
            self.extendRulesDict(ch=z[0],func=func)

    def createBracketRule (self,begin):

        i = self.brackets.index(begin)
        end = self.brackets2[i]

        def forth_bracket_rule(colorer, s, i):
            return colorer.match_span(s, i, kind="bracketRange", begin=begin, end=end,
                at_line_start=False, at_whitespace_end=False, at_word_start=False,
                delegate="",exclude_match=False,
                no_escape=False, no_line_break=False, no_word_break=False)

        return forth_bracket_rule
    #@-node:ekr.20080703111151.9:createBracketRules & helper
    #@+node:ekr.20080703111151.13:createDefiningWordRules & helper
    def createDefiningWordRules (self):

        for z in self.definingwords:
            func = self.createDefiningWordRule(z)
            self.extendRulesDict(ch=z[0],func=func)

    def createDefiningWordRule (self,word):

        def forth_defining_word_rule(colorer, s, i):
            pattern=''
            return colorer.match_word_and_regexp(s, i,
                kind1="keyword2", # defining word
                word=word,
                kind2="keyword3", # bold
                pattern='(\s)*(\S)+',
                at_line_start=False, at_whitespace_end=False, at_word_start=False,
                exclude_match=False)

        return forth_defining_word_rule
    #@-node:ekr.20080703111151.13:createDefiningWordRules & helper
    #@+node:ekr.20080703111151.6:createKeywords
    def createKeywords (self):

        '''Create the mode keyword table and
        entries in the rulesDict for the forth_keyword_rule'''

        global forth_main_keywords_dict
        global forth_keyword_rule

        table = (
            (self.keywords,         'keyword1'),
          # (self.definingwords,    'keyword2'), # Done in createDefiningWordRules.
            (self.boldwords,        'keyword3'),
            (self.bolditalicwords,  'keyword4'),
            (self.italicwords,      'keyword5'),
            (self.stringwords,      'string'),
        )

        d = forth_main_keywords_dict
        for keywordList,kind in table:
            for z in keywordList:
                # Create the entry in the keyword table.
                if kind == 'string':
                    func = self.createStringRule(z)
                    # Don't set d: the created rule handles everything.
                else:
                    func = forth_keyword_rule
                    d [z] = kind
                self.extendRulesDict(ch=z[0],func=func)
    #@-node:ekr.20080703111151.6:createKeywords
    #@+node:ekr.20080703111151.10:createStringRule
    def createStringRule (self,word):

        '''Create an entry in the global forth_main_keywords_dict for a string keyword.'''

        def forth_string_word_rule(colorer, s, i):
            return colorer.match_span(s, i, kind="literal1", begin=word, end="\"",
                at_line_start=False, at_whitespace_end=False, at_word_start=False,
                delegate="",exclude_match=False,
                no_escape=False, no_line_break=False, no_word_break=False)

        return forth_string_word_rule
    #@nonl
    #@-node:ekr.20080703111151.10:createStringRule
    #@+node:ekr.20080703111151.11:extendRulesDict
    def extendRulesDict (self,ch,func):

        global rulesDict

        # Extend the rulesDict entry for the first character of z.
        aList = rulesDict.get(ch,[])
        if func not in aList:
            aList.append(func)
            rulesDict[ch] = aList

        # g.trace(z,kind)
    #@-node:ekr.20080703111151.11:extendRulesDict
    #@-others
#@-node:ekr.20080703111151.4:<< define extendForth class >>
#@nl

extendForth()
#@-node:ekr.20080703111151.1:@thin ../modes/forth.py
#@-leo
