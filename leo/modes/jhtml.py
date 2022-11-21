# Leo colorizer control file for jhtml mode.
# This file is in the public domain.

# Properties for jhtml mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
    "indentNextLines": "\\s*(<\\s*(droplet|oparam))\\s+.*",
}

# Attributes dict for jhtml_main ruleset.
jhtml_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for jhtml_jhtml ruleset.
jhtml_jhtml_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for jhtml_attrvalue ruleset.
jhtml_attrvalue_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for jhtml mode.
attributesDictDict = {
    "jhtml_attrvalue": jhtml_attrvalue_attributes_dict,
    "jhtml_jhtml": jhtml_jhtml_attributes_dict,
    "jhtml_main": jhtml_main_attributes_dict,
}

# Keywords dict for jhtml_main ruleset.
jhtml_main_keywords_dict = {}

# Keywords dict for jhtml_jhtml ruleset.
jhtml_jhtml_keywords_dict = {
    "bean": "keyword2",
    "converter": "keyword2",
    "currency": "keyword2",
    "currencyconversion": "keyword2",
    "date": "keyword2",
    "declareparam": "keyword2",
    "droplet": "keyword1",
    "euro": "keyword2",
    "importbean": "keyword1",
    "locale": "keyword2",
    "nullable": "keyword2",
    "number": "keyword2",
    "oparam": "keyword1",
    "param": "keyword1",
    "priority": "keyword2",
    "required": "keyword2",
    "servlet": "keyword1",
    "setvalue": "keyword1",
    "submitvalue": "keyword2",
    "symbol": "keyword2",
    "synchronized": "keyword2",
    "valueof": "keyword1",
}

# Keywords dict for jhtml_attrvalue ruleset.
jhtml_attrvalue_keywords_dict = {}

# Dictionary of keywords dictionaries for jhtml mode.
keywordsDictDict = {
    "jhtml_attrvalue": jhtml_attrvalue_keywords_dict,
    "jhtml_jhtml": jhtml_jhtml_keywords_dict,
    "jhtml_main": jhtml_main_keywords_dict,
}

# Rules for jhtml_main ruleset.

def jhtml_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="null", begin="<!--#", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="`", end="`",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="java::main", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<java>", end="</java>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="java::main", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="html::css", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::dtd-tags", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="jhtml::jhtml", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=True)

# Rules dict for jhtml_main ruleset.
rulesDict1 = {
    "&": [jhtml_rule8,],
    "<": [jhtml_rule0, jhtml_rule1, jhtml_rule3, jhtml_rule4, jhtml_rule5, jhtml_rule6, jhtml_rule7,],
    "`": [jhtml_rule2,],
}

# Rules for jhtml_jhtml ruleset.

def jhtml_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="jhtml::attrvalue", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="jhtml::attrvalue", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule12(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="/",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def jhtml_rule13(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for jhtml_jhtml ruleset.
rulesDict2 = {
    "\"": [jhtml_rule10,],
    "'": [jhtml_rule11,],
    "/": [jhtml_rule12,],
    "0": [jhtml_rule13,],
    "1": [jhtml_rule13,],
    "2": [jhtml_rule13,],
    "3": [jhtml_rule13,],
    "4": [jhtml_rule13,],
    "5": [jhtml_rule13,],
    "6": [jhtml_rule13,],
    "7": [jhtml_rule13,],
    "8": [jhtml_rule13,],
    "9": [jhtml_rule13,],
    "<": [jhtml_rule9,],
    "@": [jhtml_rule13,],
    "A": [jhtml_rule13,],
    "B": [jhtml_rule13,],
    "C": [jhtml_rule13,],
    "D": [jhtml_rule13,],
    "E": [jhtml_rule13,],
    "F": [jhtml_rule13,],
    "G": [jhtml_rule13,],
    "H": [jhtml_rule13,],
    "I": [jhtml_rule13,],
    "J": [jhtml_rule13,],
    "K": [jhtml_rule13,],
    "L": [jhtml_rule13,],
    "M": [jhtml_rule13,],
    "N": [jhtml_rule13,],
    "O": [jhtml_rule13,],
    "P": [jhtml_rule13,],
    "Q": [jhtml_rule13,],
    "R": [jhtml_rule13,],
    "S": [jhtml_rule13,],
    "T": [jhtml_rule13,],
    "U": [jhtml_rule13,],
    "V": [jhtml_rule13,],
    "W": [jhtml_rule13,],
    "X": [jhtml_rule13,],
    "Y": [jhtml_rule13,],
    "Z": [jhtml_rule13,],
    "a": [jhtml_rule13,],
    "b": [jhtml_rule13,],
    "c": [jhtml_rule13,],
    "d": [jhtml_rule13,],
    "e": [jhtml_rule13,],
    "f": [jhtml_rule13,],
    "g": [jhtml_rule13,],
    "h": [jhtml_rule13,],
    "i": [jhtml_rule13,],
    "j": [jhtml_rule13,],
    "k": [jhtml_rule13,],
    "l": [jhtml_rule13,],
    "m": [jhtml_rule13,],
    "n": [jhtml_rule13,],
    "o": [jhtml_rule13,],
    "p": [jhtml_rule13,],
    "q": [jhtml_rule13,],
    "r": [jhtml_rule13,],
    "s": [jhtml_rule13,],
    "t": [jhtml_rule13,],
    "u": [jhtml_rule13,],
    "v": [jhtml_rule13,],
    "w": [jhtml_rule13,],
    "x": [jhtml_rule13,],
    "y": [jhtml_rule13,],
    "z": [jhtml_rule13,],
}

# Rules for jhtml_attrvalue ruleset.

def jhtml_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="`", end="`",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="java::main", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def jhtml_rule15(colorer, s, i):
    return colorer.match_seq(s, i, kind="label", seq="param:",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def jhtml_rule16(colorer, s, i):
    return colorer.match_seq(s, i, kind="label", seq="bean:",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for jhtml_attrvalue ruleset.
rulesDict3 = {
    "`": [jhtml_rule14,],
    "b": [jhtml_rule16,],
    "p": [jhtml_rule15,],
}

# x.rulesDictDict for jhtml mode.
rulesDictDict = {
    "jhtml_attrvalue": rulesDict3,
    "jhtml_jhtml": rulesDict2,
    "jhtml_main": rulesDict1,
}

# Import dict for jhtml mode.
importDict = {}
