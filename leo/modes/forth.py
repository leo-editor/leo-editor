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
        at_line_start=False, at_whitespace_end=False, at_word_start=True, # Require word.
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def forth_comment_rule(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="\\",
        at_line_start=False, at_whitespace_end=False, at_word_start=True, # Require word
        delegate="", exclude_match=False)

def forth_keyword_rule(colorer, s, i):
    return colorer.match_keywords(s, i)

def forth_string_rule(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=True, # Require word
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

        # g.trace('modes/forth.py:extendForth')

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
            # Must be pairs.
            '" "',
            ]
        self.stringwords1 = []
        self.stringwords2 = []

        self.verbose = False # True: tell when extending forth words.

        self.init()
        self.createKeywords()
        self.createBracketRules()
        self.createDefiningWordRules()
        # g.trace('rulesDict...\n',g.dictToString(rulesDict),tag='rulesDict...')
    #@-node:ekr.20080703111151.5:ctor
    #@+node:ekr.20080703111151.3:init & helper
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
        for (lst, path, message) in table:
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
                            print "Found extra forth %s" % message + ": " + " ".join(extras)
                    lst.extend(extras)
            except IOError:
                pass # print "Not found",path

        # Create brackets1/2 and stringwords1/2 lists.
        table2 = (
            ("brackets",    "leo-forthdelimiters.txt"),
            ("stringwords", "leo-forthstringwords.txt"),
        )
        for (ivar, fileName) in table2:
            self.splitList (ivar,fileName)
    #@+node:ekr.20080704085627.2:splitList
    def splitList (self,ivar,fileName):

        '''Process lines containing pairs of entries 
        in a list whose *name* is ivar.
        Put the results in ivars whose names are ivar1 and ivar2.'''

        result1 = [] ; result2 = []
        aList = getattr(self,ivar)

        # Look for pairs.  Comments have already been removed.
        for s in aList:
            pair = s.split(' ')
            if len(pair) == 2 and pair[0].strip() and pair[1].strip():
                result1.append(pair[0].strip())
                result2.append(pair[1].strip())
            else:
                g.es_print('%s: ignoring line: %s' % (fileName,s))

        # Set the ivars.
        name1 = '%s1' % ivar
        name2 = '%s2' % ivar
        setattr(self,name1, result1)
        setattr(self,name2, result2)

        # g.trace(name1,getattr(self,name1))
        # g.trace(name2,getattr(self,name2))
    #@nonl
    #@-node:ekr.20080704085627.2:splitList
    #@-node:ekr.20080703111151.3:init & helper
    #@+node:ekr.20080703111151.9:createBracketRules & helper
    def createBracketRules (self):

        for z in self.brackets1:
            func = self.createBracketRule(z)
            self.extendRulesDict(ch=z[0],func=func)

    def createBracketRule (self,begin):

        i = self.brackets1.index(begin)
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
                    func = self.createStringRule(d,z)
                else:
                    func = forth_keyword_rule

                # Always make the entry.
                d [z] = kind
                self.extendRulesDict(ch=z[0],func=func)
    #@-node:ekr.20080703111151.6:createKeywords
    #@+node:ekr.20080703111151.10:createStringRule
    def createStringRule (self,d,pair):

        '''Create an entry in d for a string keyword.'''

        aList = pair.split(' ')
        if len(aList) != 2:
            g.trace('can not happen: expecting pair of forth strings:',pair)
            return

        begin,end = aList

        def forth_string_word_rule(colorer, s, i):
            return colorer.match_span(s, i, kind="literal1", begin=begin.strip(), end=end.strip(),
                at_line_start=False, at_whitespace_end=False, at_word_start=True, # Require word.
                delegate="",exclude_match=False,
                no_escape=False, no_line_break=False, no_word_break=False)

        return forth_string_word_rule
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
