# Leo colorizer control file for ptl mode.
# This file is in the public domain.

# Properties for ptl mode.
properties = {
    "indentNextLines": "\\s*[^#]{3,}:\\s*(#.*)?",
    "lineComment": "#",
}

# Attributes dict for ptl_main ruleset.
ptl_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for ptl mode.
attributesDictDict = {
    "ptl_main": ptl_main_attributes_dict,
}

# Keywords dict for ptl_main ruleset.
ptl_main_keywords_dict = {
    "_q_access": "literal4",
    "_q_exception_handler": "literal4",
    "_q_exports": "literal4",
    "_q_index": "literal4",
    "_q_lookup": "literal4",
    "_q_resolve": "literal4",
}

# Dictionary of keywords dictionaries for ptl mode.
keywordsDictDict = {
    "ptl_main": ptl_main_keywords_dict,
}

# Rules for ptl_main ruleset.


def ptl_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword4", seq="[html]")

def ptl_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword4", seq="[plain]")

def ptl_rule2(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for ptl_main ruleset.
rulesDict1 = {
    "0": [ptl_rule2,],
    "1": [ptl_rule2,],
    "2": [ptl_rule2,],
    "3": [ptl_rule2,],
    "4": [ptl_rule2,],
    "5": [ptl_rule2,],
    "6": [ptl_rule2,],
    "7": [ptl_rule2,],
    "8": [ptl_rule2,],
    "9": [ptl_rule2,],
    "@": [ptl_rule2,],
    "A": [ptl_rule2,],
    "B": [ptl_rule2,],
    "C": [ptl_rule2,],
    "D": [ptl_rule2,],
    "E": [ptl_rule2,],
    "F": [ptl_rule2,],
    "G": [ptl_rule2,],
    "H": [ptl_rule2,],
    "I": [ptl_rule2,],
    "J": [ptl_rule2,],
    "K": [ptl_rule2,],
    "L": [ptl_rule2,],
    "M": [ptl_rule2,],
    "N": [ptl_rule2,],
    "O": [ptl_rule2,],
    "P": [ptl_rule2,],
    "Q": [ptl_rule2,],
    "R": [ptl_rule2,],
    "S": [ptl_rule2,],
    "T": [ptl_rule2,],
    "U": [ptl_rule2,],
    "V": [ptl_rule2,],
    "W": [ptl_rule2,],
    "X": [ptl_rule2,],
    "Y": [ptl_rule2,],
    "Z": [ptl_rule2,],
    "[": [ptl_rule0, ptl_rule1,],
    "_": [ptl_rule2,],
    "a": [ptl_rule2,],
    "b": [ptl_rule2,],
    "c": [ptl_rule2,],
    "d": [ptl_rule2,],
    "e": [ptl_rule2,],
    "f": [ptl_rule2,],
    "g": [ptl_rule2,],
    "h": [ptl_rule2,],
    "i": [ptl_rule2,],
    "j": [ptl_rule2,],
    "k": [ptl_rule2,],
    "l": [ptl_rule2,],
    "m": [ptl_rule2,],
    "n": [ptl_rule2,],
    "o": [ptl_rule2,],
    "p": [ptl_rule2,],
    "q": [ptl_rule2,],
    "r": [ptl_rule2,],
    "s": [ptl_rule2,],
    "t": [ptl_rule2,],
    "u": [ptl_rule2,],
    "v": [ptl_rule2,],
    "w": [ptl_rule2,],
    "x": [ptl_rule2,],
    "y": [ptl_rule2,],
    "z": [ptl_rule2,],
}

# x.rulesDictDict for ptl mode.
rulesDictDict = {
    "ptl_main": rulesDict1,
}

# Import dict for ptl mode.
importDict = {
    "ptl_main": ["python::main",],
}
