# Leo colorizer control file for shtml mode.
# This file is in the public domain.

# Properties for shtml mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

# Attributes dict for shtml_main ruleset.
shtml_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for shtml_tags ruleset.
shtml_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for shtml_ssi ruleset.
shtml_ssi_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for shtml_ssi_expression ruleset.
shtml_ssi_expression_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for shtml mode.
attributesDictDict = {
    "shtml_main": shtml_main_attributes_dict,
    "shtml_ssi": shtml_ssi_attributes_dict,
    "shtml_ssi_expression": shtml_ssi_expression_attributes_dict,
    "shtml_tags": shtml_tags_attributes_dict,
}

# Keywords dict for shtml_main ruleset.
shtml_main_keywords_dict = {}

# Keywords dict for shtml_tags ruleset.
shtml_tags_keywords_dict = {}

# Keywords dict for shtml_ssi ruleset.
shtml_ssi_keywords_dict = {
    "cgi": "keyword2",
    "cmd": "keyword2",
    "config": "keyword1",
    "echo": "keyword1",
    "errmsg": "keyword2",
    "exec": "keyword1",
    "file": "keyword2",
    "flastmod": "keyword1",
    "fsize": "keyword1",
    "include": "keyword1",
    "sizefmt": "keyword2",
    "timefmt": "keyword2",
    "var": "keyword2",
}

# Keywords dict for shtml_ssi_expression ruleset.
shtml_ssi_expression_keywords_dict = {}

# Dictionary of keywords dictionaries for shtml mode.
keywordsDictDict = {
    "shtml_main": shtml_main_keywords_dict,
    "shtml_ssi": shtml_ssi_keywords_dict,
    "shtml_ssi_expression": shtml_ssi_expression_keywords_dict,
    "shtml_tags": shtml_tags_keywords_dict,
}

# Rules for shtml_main ruleset.

def shtml_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="<!--#", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="shtml::ssi", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def shtml_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def shtml_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def shtml_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::css", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def shtml_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::dtd-tags", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def shtml_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="shtml::tags", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def shtml_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=True)

# Rules dict for shtml_main ruleset.
rulesDict1 = {
    "&": [shtml_rule6,],
    "<": [shtml_rule0, shtml_rule1, shtml_rule2, shtml_rule3, shtml_rule4, shtml_rule5,],
}

# Rules for shtml_tags ruleset.

def shtml_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def shtml_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def shtml_rule9(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for shtml_tags ruleset.
rulesDict2 = {
    "\"": [shtml_rule7,],
    "'": [shtml_rule8,],
    "=": [shtml_rule9,],
}

# Rules for shtml_ssi ruleset.

def shtml_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="shtml::ssi-expression", exclude_match=True,
        no_escape=False, no_line_break=False, no_word_break=False)

def shtml_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def shtml_rule12(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for shtml_ssi ruleset.
rulesDict3 = {
    "\"": [shtml_rule10,],
    "0": [shtml_rule12,],
    "1": [shtml_rule12,],
    "2": [shtml_rule12,],
    "3": [shtml_rule12,],
    "4": [shtml_rule12,],
    "5": [shtml_rule12,],
    "6": [shtml_rule12,],
    "7": [shtml_rule12,],
    "8": [shtml_rule12,],
    "9": [shtml_rule12,],
    "=": [shtml_rule11,],
    "@": [shtml_rule12,],
    "A": [shtml_rule12,],
    "B": [shtml_rule12,],
    "C": [shtml_rule12,],
    "D": [shtml_rule12,],
    "E": [shtml_rule12,],
    "F": [shtml_rule12,],
    "G": [shtml_rule12,],
    "H": [shtml_rule12,],
    "I": [shtml_rule12,],
    "J": [shtml_rule12,],
    "K": [shtml_rule12,],
    "L": [shtml_rule12,],
    "M": [shtml_rule12,],
    "N": [shtml_rule12,],
    "O": [shtml_rule12,],
    "P": [shtml_rule12,],
    "Q": [shtml_rule12,],
    "R": [shtml_rule12,],
    "S": [shtml_rule12,],
    "T": [shtml_rule12,],
    "U": [shtml_rule12,],
    "V": [shtml_rule12,],
    "W": [shtml_rule12,],
    "X": [shtml_rule12,],
    "Y": [shtml_rule12,],
    "Z": [shtml_rule12,],
    "a": [shtml_rule12,],
    "b": [shtml_rule12,],
    "c": [shtml_rule12,],
    "d": [shtml_rule12,],
    "e": [shtml_rule12,],
    "f": [shtml_rule12,],
    "g": [shtml_rule12,],
    "h": [shtml_rule12,],
    "i": [shtml_rule12,],
    "j": [shtml_rule12,],
    "k": [shtml_rule12,],
    "l": [shtml_rule12,],
    "m": [shtml_rule12,],
    "n": [shtml_rule12,],
    "o": [shtml_rule12,],
    "p": [shtml_rule12,],
    "q": [shtml_rule12,],
    "r": [shtml_rule12,],
    "s": [shtml_rule12,],
    "t": [shtml_rule12,],
    "u": [shtml_rule12,],
    "v": [shtml_rule12,],
    "w": [shtml_rule12,],
    "x": [shtml_rule12,],
    "y": [shtml_rule12,],
    "z": [shtml_rule12,],
}

# Rules for shtml_ssi_expression ruleset.

def shtml_rule13(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def shtml_rule14(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def shtml_rule15(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="!=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def shtml_rule16(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="<",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def shtml_rule17(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="<=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def shtml_rule18(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def shtml_rule19(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=">=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def shtml_rule20(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="&&",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def shtml_rule21(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="||",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for shtml_ssi_expression ruleset.
rulesDict4 = {
    "!": [shtml_rule15,],
    "$": [shtml_rule13,],
    "&": [shtml_rule20,],
    "<": [shtml_rule16, shtml_rule17,],
    "=": [shtml_rule14,],
    ">": [shtml_rule18, shtml_rule19,],
    "|": [shtml_rule21,],
}

# x.rulesDictDict for shtml mode.
rulesDictDict = {
    "shtml_main": rulesDict1,
    "shtml_ssi": rulesDict3,
    "shtml_ssi_expression": rulesDict4,
    "shtml_tags": rulesDict2,
}

# Import dict for shtml mode.
importDict = {}
