# Leo colorizer control file for pyrex mode.
# This file is in the public domain.

# Properties for pyrex mode.
properties = {
    "indentNextLines": "\\s*[^#]{3,}:\\s*(#.*)?",
    "lineComment": "#",
}

# Attributes dict for pyrex_main ruleset.
pyrex_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for pyrex mode.
attributesDictDict = {
    "pyrex_main": pyrex_main_attributes_dict,
}

# Keywords dict for pyrex_main ruleset.
pyrex_main_keywords_dict = {
    "NULL": "literal3",
    "cdef": "keyword4",
    "char": "keyword4",
    "cinclude": "keyword4",
    "ctypedef": "keyword4",
    "double": "keyword4",
    "enum": "keyword4",
    "extern": "keyword4",
    "float": "keyword4",
    "include": "keyword4",
    "private": "keyword4",
    "public": "keyword4",
    "short": "keyword4",
    "signed": "keyword4",
    "sizeof": "keyword4",
    "struct": "keyword4",
    "union": "keyword4",
    "unsigned": "keyword4",
    "void": "keyword4",
}

# Dictionary of keywords dictionaries for pyrex mode.
keywordsDictDict = {
    "pyrex_main": pyrex_main_keywords_dict,
}

# Rules for pyrex_main ruleset.


def pyrex_rule0(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for pyrex_main ruleset.
rulesDict1 = {
    "0": [pyrex_rule0,],
    "1": [pyrex_rule0,],
    "2": [pyrex_rule0,],
    "3": [pyrex_rule0,],
    "4": [pyrex_rule0,],
    "5": [pyrex_rule0,],
    "6": [pyrex_rule0,],
    "7": [pyrex_rule0,],
    "8": [pyrex_rule0,],
    "9": [pyrex_rule0,],
    "@": [pyrex_rule0,],
    "A": [pyrex_rule0,],
    "B": [pyrex_rule0,],
    "C": [pyrex_rule0,],
    "D": [pyrex_rule0,],
    "E": [pyrex_rule0,],
    "F": [pyrex_rule0,],
    "G": [pyrex_rule0,],
    "H": [pyrex_rule0,],
    "I": [pyrex_rule0,],
    "J": [pyrex_rule0,],
    "K": [pyrex_rule0,],
    "L": [pyrex_rule0,],
    "M": [pyrex_rule0,],
    "N": [pyrex_rule0,],
    "O": [pyrex_rule0,],
    "P": [pyrex_rule0,],
    "Q": [pyrex_rule0,],
    "R": [pyrex_rule0,],
    "S": [pyrex_rule0,],
    "T": [pyrex_rule0,],
    "U": [pyrex_rule0,],
    "V": [pyrex_rule0,],
    "W": [pyrex_rule0,],
    "X": [pyrex_rule0,],
    "Y": [pyrex_rule0,],
    "Z": [pyrex_rule0,],
    "a": [pyrex_rule0,],
    "b": [pyrex_rule0,],
    "c": [pyrex_rule0,],
    "d": [pyrex_rule0,],
    "e": [pyrex_rule0,],
    "f": [pyrex_rule0,],
    "g": [pyrex_rule0,],
    "h": [pyrex_rule0,],
    "i": [pyrex_rule0,],
    "j": [pyrex_rule0,],
    "k": [pyrex_rule0,],
    "l": [pyrex_rule0,],
    "m": [pyrex_rule0,],
    "n": [pyrex_rule0,],
    "o": [pyrex_rule0,],
    "p": [pyrex_rule0,],
    "q": [pyrex_rule0,],
    "r": [pyrex_rule0,],
    "s": [pyrex_rule0,],
    "t": [pyrex_rule0,],
    "u": [pyrex_rule0,],
    "v": [pyrex_rule0,],
    "w": [pyrex_rule0,],
    "x": [pyrex_rule0,],
    "y": [pyrex_rule0,],
    "z": [pyrex_rule0,],
}

# x.rulesDictDict for pyrex mode.
rulesDictDict = {
    "pyrex_main": rulesDict1,
}

# Import dict for pyrex mode.
importDict = {
    "pyrex_main": ["python::main",],
}
