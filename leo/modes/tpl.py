# Leo colorizer control file for tpl mode.
# This file is in the public domain.

# Properties for tpl mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

# Attributes dict for tpl_main ruleset.
tpl_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for tpl_tpl ruleset.
tpl_tpl_attributes_dict = {
    "default": "KEYWORD1",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for tpl_tags ruleset.
tpl_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for tpl mode.
attributesDictDict = {
    "tpl_main": tpl_main_attributes_dict,
    "tpl_tags": tpl_tags_attributes_dict,
    "tpl_tpl": tpl_tpl_attributes_dict,
}

# Keywords dict for tpl_main ruleset.
tpl_main_keywords_dict = {}

# Keywords dict for tpl_tpl ruleset.
tpl_tpl_keywords_dict = {
    "=": "operator",
    "end": "keyword2",
    "include": "keyword1",
    "start": "keyword2",
}

# Keywords dict for tpl_tags ruleset.
tpl_tags_keywords_dict = {}

# Dictionary of keywords dictionaries for tpl mode.
keywordsDictDict = {
    "tpl_main": tpl_main_keywords_dict,
    "tpl_tags": tpl_tags_keywords_dict,
    "tpl_tpl": tpl_tpl_keywords_dict,
}

# Rules for tpl_main ruleset.

def tpl_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="<!--", end="-->")

def tpl_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
          delegate="html::javascript")

def tpl_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
          delegate="html::css")

def tpl_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="tpl::tags")

def tpl_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

def tpl_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="{", end="}",
          delegate="tpl::tpl")

# Rules dict for tpl_main ruleset.
rulesDict1 = {
    "&": [tpl_rule4,],
    "<": [tpl_rule0, tpl_rule1, tpl_rule2, tpl_rule3,],
    "{": [tpl_rule5,],
}

# Rules for tpl_tpl ruleset.

def tpl_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="\"", end="\"")

def tpl_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="'", end="'")

def tpl_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def tpl_rule9(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for tpl_tpl ruleset.
rulesDict2 = {
    "\"": [tpl_rule6,],
    "'": [tpl_rule7,],
    "*": [tpl_rule8,],
    "0": [tpl_rule9,],
    "1": [tpl_rule9,],
    "2": [tpl_rule9,],
    "3": [tpl_rule9,],
    "4": [tpl_rule9,],
    "5": [tpl_rule9,],
    "6": [tpl_rule9,],
    "7": [tpl_rule9,],
    "8": [tpl_rule9,],
    "9": [tpl_rule9,],
    "=": [tpl_rule9,],
    "@": [tpl_rule9,],
    "A": [tpl_rule9,],
    "B": [tpl_rule9,],
    "C": [tpl_rule9,],
    "D": [tpl_rule9,],
    "E": [tpl_rule9,],
    "F": [tpl_rule9,],
    "G": [tpl_rule9,],
    "H": [tpl_rule9,],
    "I": [tpl_rule9,],
    "J": [tpl_rule9,],
    "K": [tpl_rule9,],
    "L": [tpl_rule9,],
    "M": [tpl_rule9,],
    "N": [tpl_rule9,],
    "O": [tpl_rule9,],
    "P": [tpl_rule9,],
    "Q": [tpl_rule9,],
    "R": [tpl_rule9,],
    "S": [tpl_rule9,],
    "T": [tpl_rule9,],
    "U": [tpl_rule9,],
    "V": [tpl_rule9,],
    "W": [tpl_rule9,],
    "X": [tpl_rule9,],
    "Y": [tpl_rule9,],
    "Z": [tpl_rule9,],
    "a": [tpl_rule9,],
    "b": [tpl_rule9,],
    "c": [tpl_rule9,],
    "d": [tpl_rule9,],
    "e": [tpl_rule9,],
    "f": [tpl_rule9,],
    "g": [tpl_rule9,],
    "h": [tpl_rule9,],
    "i": [tpl_rule9,],
    "j": [tpl_rule9,],
    "k": [tpl_rule9,],
    "l": [tpl_rule9,],
    "m": [tpl_rule9,],
    "n": [tpl_rule9,],
    "o": [tpl_rule9,],
    "p": [tpl_rule9,],
    "q": [tpl_rule9,],
    "r": [tpl_rule9,],
    "s": [tpl_rule9,],
    "t": [tpl_rule9,],
    "u": [tpl_rule9,],
    "v": [tpl_rule9,],
    "w": [tpl_rule9,],
    "x": [tpl_rule9,],
    "y": [tpl_rule9,],
    "z": [tpl_rule9,],
}

# Rules for tpl_tags ruleset.

def tpl_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def tpl_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def tpl_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

# Rules dict for tpl_tags ruleset.
rulesDict3 = {
    "\"": [tpl_rule10,],
    "'": [tpl_rule11,],
    "=": [tpl_rule12,],
}

# x.rulesDictDict for tpl mode.
rulesDictDict = {
    "tpl_main": rulesDict1,
    "tpl_tags": rulesDict3,
    "tpl_tpl": rulesDict2,
}

# Import dict for tpl mode.
importDict = {}
