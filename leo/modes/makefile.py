# Leo colorizer control file for makefile mode.
# This file is in the public domain.

# Properties for makefile mode.
properties = {
    "lineComment": "#",
}

# Attributes dict for makefile_main ruleset.
makefile_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for makefile_variable ruleset.
makefile_variable_attributes_dict = {
    "default": "KEYWORD2",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for makefile mode.
attributesDictDict = {
    "makefile_main": makefile_main_attributes_dict,
    "makefile_variable": makefile_variable_attributes_dict,
}

# Keywords dict for makefile_main ruleset.
makefile_main_keywords_dict = {
    "addprefix": "keyword1",
    "addsuffix": "keyword1",
    "basename": "keyword1",
    "dir": "keyword1",
    "filter": "keyword1",
    "filter-out": "keyword1",
    "findstring": "keyword1",
    "firstword": "keyword1",
    "foreach": "keyword1",
    "join": "keyword1",
    "notdir": "keyword1",
    "origin": "keyword1",
    "patsubst": "keyword1",
    "shell": "keyword1",
    "sort": "keyword1",
    "strip": "keyword1",
    "subst": "keyword1",
    "suffix": "keyword1",
    "wildcard": "keyword1",
    "word": "keyword1",
    "words": "keyword1",
}

# Keywords dict for makefile_variable ruleset.
makefile_variable_keywords_dict = {}

# Dictionary of keywords dictionaries for makefile mode.
keywordsDictDict = {
    "makefile_main": makefile_main_keywords_dict,
    "makefile_variable": makefile_variable_keywords_dict,
}

# Rules for makefile_main ruleset.

def makefile_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def makefile_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="$(", end=")",
          delegate="makefile::variable",
          no_line_break=True)

def makefile_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          delegate="makefile::variable",
          no_line_break=True)

def makefile_rule3(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$")

def makefile_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def makefile_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def makefile_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="`", end="`",
          no_line_break=True)

def makefile_rule7(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":")

def makefile_rule8(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for makefile_main ruleset.
rulesDict1 = {
    "\"": [makefile_rule4,],
    "#": [makefile_rule0,],
    "$": [makefile_rule1, makefile_rule2, makefile_rule3,],
    "'": [makefile_rule5,],
    "-": [makefile_rule8,],
    "0": [makefile_rule8,],
    "1": [makefile_rule8,],
    "2": [makefile_rule8,],
    "3": [makefile_rule8,],
    "4": [makefile_rule8,],
    "5": [makefile_rule8,],
    "6": [makefile_rule8,],
    "7": [makefile_rule8,],
    "8": [makefile_rule8,],
    "9": [makefile_rule8,],
    ":": [makefile_rule7,],
    "@": [makefile_rule8,],
    "A": [makefile_rule8,],
    "B": [makefile_rule8,],
    "C": [makefile_rule8,],
    "D": [makefile_rule8,],
    "E": [makefile_rule8,],
    "F": [makefile_rule8,],
    "G": [makefile_rule8,],
    "H": [makefile_rule8,],
    "I": [makefile_rule8,],
    "J": [makefile_rule8,],
    "K": [makefile_rule8,],
    "L": [makefile_rule8,],
    "M": [makefile_rule8,],
    "N": [makefile_rule8,],
    "O": [makefile_rule8,],
    "P": [makefile_rule8,],
    "Q": [makefile_rule8,],
    "R": [makefile_rule8,],
    "S": [makefile_rule8,],
    "T": [makefile_rule8,],
    "U": [makefile_rule8,],
    "V": [makefile_rule8,],
    "W": [makefile_rule8,],
    "X": [makefile_rule8,],
    "Y": [makefile_rule8,],
    "Z": [makefile_rule8,],
    "`": [makefile_rule6,],
    "a": [makefile_rule8,],
    "b": [makefile_rule8,],
    "c": [makefile_rule8,],
    "d": [makefile_rule8,],
    "e": [makefile_rule8,],
    "f": [makefile_rule8,],
    "g": [makefile_rule8,],
    "h": [makefile_rule8,],
    "i": [makefile_rule8,],
    "j": [makefile_rule8,],
    "k": [makefile_rule8,],
    "l": [makefile_rule8,],
    "m": [makefile_rule8,],
    "n": [makefile_rule8,],
    "o": [makefile_rule8,],
    "p": [makefile_rule8,],
    "q": [makefile_rule8,],
    "r": [makefile_rule8,],
    "s": [makefile_rule8,],
    "t": [makefile_rule8,],
    "u": [makefile_rule8,],
    "v": [makefile_rule8,],
    "w": [makefile_rule8,],
    "x": [makefile_rule8,],
    "y": [makefile_rule8,],
    "z": [makefile_rule8,],
}

# Rules for makefile_variable ruleset.

def makefile_rule9(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def makefile_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="$(", end=")",
          delegate="makefile::variable",
          no_line_break=True)

def makefile_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          delegate="makefile::variable",
          no_line_break=True)

# Rules dict for makefile_variable ruleset.
rulesDict2 = {
    "#": [makefile_rule9,],
    "$": [makefile_rule10, makefile_rule11,],
}

# x.rulesDictDict for makefile mode.
rulesDictDict = {
    "makefile_main": rulesDict1,
    "makefile_variable": rulesDict2,
}

# Import dict for makefile mode.
importDict = {}
