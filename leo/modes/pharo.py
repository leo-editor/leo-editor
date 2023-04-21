# Leo colorizer control file for pharo mode.
# This file is in the public domain.

# Properties for pharo mode.
properties = {
    "commentEnd": "\"",
    "commentStart": "\"",
    "indentCloseBrackets": "]",
    "indentOpenBrackets": "[",
    "lineUpClosingBracket": "true",
}

# Attributes dict for pharo_main ruleset.
pharo_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for pharo mode.
attributesDictDict = {
    "pharo_main": pharo_main_attributes_dict,
}

# Keywords dict for pharo_main ruleset.
pharo_main_keywords_dict = {
    "Array": "literal2",
    "Boolean": "literal2",
    "Character": "literal2",
    "Date": "literal2",
    "False": "literal2",
    "Integer": "literal2",
    "Object": "literal2",
    "pharo": "literal2",
    "String": "literal2",
    "Symbol": "literal2",
    "Time": "literal2",
    "Transcript": "literal2",
    "True": "literal2",
    "false": "keyword1",
    "isNil": "keyword3",
    "nil": "keyword1",
    "not": "keyword3",
    "self": "keyword2",
    "super": "keyword2",
    "true": "keyword1",
}

# Dictionary of keywords dictionaries for pharo mode.
keywordsDictDict = {
    "pharo_main": pharo_main_keywords_dict,
}

# Rules for pharo_main ruleset.

def pharo_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def pharo_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="\"", end="\"")

def pharo_rule2(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def pharo_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="_")

def pharo_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def pharo_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def pharo_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def pharo_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def pharo_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def pharo_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def pharo_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def pharo_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def pharo_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def pharo_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def pharo_rule14(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="keyword3", pattern=":",
          exclude_match=True)

def pharo_rule15(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="label", pattern="#",
          exclude_match=True)

def pharo_rule16(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="$",
          exclude_match=True)

def pharo_rule17(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for pharo_main ruleset.
rulesDict1 = {
    "\"": [pharo_rule1,],
    "#": [pharo_rule15,],
    "$": [pharo_rule16,],
    "'": [pharo_rule0,],
    "*": [pharo_rule13,],
    "+": [pharo_rule10,],
    "-": [pharo_rule11,],
    "/": [pharo_rule12,],
    "0": [pharo_rule17,],
    "1": [pharo_rule17,],
    "2": [pharo_rule17,],
    "3": [pharo_rule17,],
    "4": [pharo_rule17,],
    "5": [pharo_rule17,],
    "6": [pharo_rule17,],
    "7": [pharo_rule17,],
    "8": [pharo_rule17,],
    "9": [pharo_rule17,],
    ":": [pharo_rule2, pharo_rule14,],
    "<": [pharo_rule7, pharo_rule9,],
    "=": [pharo_rule4, pharo_rule5,],
    ">": [pharo_rule6, pharo_rule8,],
    "@": [pharo_rule17,],
    "A": [pharo_rule17,],
    "B": [pharo_rule17,],
    "C": [pharo_rule17,],
    "D": [pharo_rule17,],
    "E": [pharo_rule17,],
    "F": [pharo_rule17,],
    "G": [pharo_rule17,],
    "H": [pharo_rule17,],
    "I": [pharo_rule17,],
    "J": [pharo_rule17,],
    "K": [pharo_rule17,],
    "L": [pharo_rule17,],
    "M": [pharo_rule17,],
    "N": [pharo_rule17,],
    "O": [pharo_rule17,],
    "P": [pharo_rule17,],
    "Q": [pharo_rule17,],
    "R": [pharo_rule17,],
    "S": [pharo_rule17,],
    "T": [pharo_rule17,],
    "U": [pharo_rule17,],
    "V": [pharo_rule17,],
    "W": [pharo_rule17,],
    "X": [pharo_rule17,],
    "Y": [pharo_rule17,],
    "Z": [pharo_rule17,],
    "_": [pharo_rule3,],
    "a": [pharo_rule17,],
    "b": [pharo_rule17,],
    "c": [pharo_rule17,],
    "d": [pharo_rule17,],
    "e": [pharo_rule17,],
    "f": [pharo_rule17,],
    "g": [pharo_rule17,],
    "h": [pharo_rule17,],
    "i": [pharo_rule17,],
    "j": [pharo_rule17,],
    "k": [pharo_rule17,],
    "l": [pharo_rule17,],
    "m": [pharo_rule17,],
    "n": [pharo_rule17,],
    "o": [pharo_rule17,],
    "p": [pharo_rule17,],
    "q": [pharo_rule17,],
    "r": [pharo_rule17,],
    "s": [pharo_rule17,],
    "t": [pharo_rule17,],
    "u": [pharo_rule17,],
    "v": [pharo_rule17,],
    "w": [pharo_rule17,],
    "x": [pharo_rule17,],
    "y": [pharo_rule17,],
    "z": [pharo_rule17,],
}

# x.rulesDictDict for pharo mode.
rulesDictDict = {
    "pharo_main": rulesDict1,
}

# Import dict for pharo mode.
importDict = {}
