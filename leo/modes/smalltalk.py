# Leo colorizer control file for smalltalk mode.
# This file is in the public domain.

# Properties for smalltalk mode.
properties = {
    "commentEnd": "\"",
    "commentStart": "\"",
    "indentCloseBrackets": "]",
    "indentOpenBrackets": "[",
    "lineUpClosingBracket": "true",
}

# Attributes dict for smalltalk_main ruleset.
smalltalk_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for smalltalk mode.
attributesDictDict = {
    "smalltalk_main": smalltalk_main_attributes_dict,
}

# Keywords dict for smalltalk_main ruleset.
smalltalk_main_keywords_dict = {
    "Array": "literal2",
    "Boolean": "literal2",
    "Character": "literal2",
    "Date": "literal2",
    "False": "literal2",
    "Integer": "literal2",
    "Object": "literal2",
    "Smalltalk": "literal2",
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

# Dictionary of keywords dictionaries for smalltalk mode.
keywordsDictDict = {
    "smalltalk_main": smalltalk_main_keywords_dict,
}

# Rules for smalltalk_main ruleset.

def smalltalk_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def smalltalk_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="\"", end="\"")

def smalltalk_rule2(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def smalltalk_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="_")

def smalltalk_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def smalltalk_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def smalltalk_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def smalltalk_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def smalltalk_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def smalltalk_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def smalltalk_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def smalltalk_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def smalltalk_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def smalltalk_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def smalltalk_rule14(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="keyword3", pattern=":",
          exclude_match=True)

def smalltalk_rule15(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="label", pattern="#",
          exclude_match=True)

def smalltalk_rule16(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="$",
          exclude_match=True)

def smalltalk_rule17(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for smalltalk_main ruleset.
rulesDict1 = {
    "\"": [smalltalk_rule1,],
    "#": [smalltalk_rule15,],
    "$": [smalltalk_rule16,],
    "'": [smalltalk_rule0,],
    "*": [smalltalk_rule13,],
    "+": [smalltalk_rule10,],
    "-": [smalltalk_rule11,],
    "/": [smalltalk_rule12,],
    "0": [smalltalk_rule17,],
    "1": [smalltalk_rule17,],
    "2": [smalltalk_rule17,],
    "3": [smalltalk_rule17,],
    "4": [smalltalk_rule17,],
    "5": [smalltalk_rule17,],
    "6": [smalltalk_rule17,],
    "7": [smalltalk_rule17,],
    "8": [smalltalk_rule17,],
    "9": [smalltalk_rule17,],
    ":": [smalltalk_rule2, smalltalk_rule14,],
    "<": [smalltalk_rule7, smalltalk_rule9,],
    "=": [smalltalk_rule4, smalltalk_rule5,],
    ">": [smalltalk_rule6, smalltalk_rule8,],
    "@": [smalltalk_rule17,],
    "A": [smalltalk_rule17,],
    "B": [smalltalk_rule17,],
    "C": [smalltalk_rule17,],
    "D": [smalltalk_rule17,],
    "E": [smalltalk_rule17,],
    "F": [smalltalk_rule17,],
    "G": [smalltalk_rule17,],
    "H": [smalltalk_rule17,],
    "I": [smalltalk_rule17,],
    "J": [smalltalk_rule17,],
    "K": [smalltalk_rule17,],
    "L": [smalltalk_rule17,],
    "M": [smalltalk_rule17,],
    "N": [smalltalk_rule17,],
    "O": [smalltalk_rule17,],
    "P": [smalltalk_rule17,],
    "Q": [smalltalk_rule17,],
    "R": [smalltalk_rule17,],
    "S": [smalltalk_rule17,],
    "T": [smalltalk_rule17,],
    "U": [smalltalk_rule17,],
    "V": [smalltalk_rule17,],
    "W": [smalltalk_rule17,],
    "X": [smalltalk_rule17,],
    "Y": [smalltalk_rule17,],
    "Z": [smalltalk_rule17,],
    "_": [smalltalk_rule3,],
    "a": [smalltalk_rule17,],
    "b": [smalltalk_rule17,],
    "c": [smalltalk_rule17,],
    "d": [smalltalk_rule17,],
    "e": [smalltalk_rule17,],
    "f": [smalltalk_rule17,],
    "g": [smalltalk_rule17,],
    "h": [smalltalk_rule17,],
    "i": [smalltalk_rule17,],
    "j": [smalltalk_rule17,],
    "k": [smalltalk_rule17,],
    "l": [smalltalk_rule17,],
    "m": [smalltalk_rule17,],
    "n": [smalltalk_rule17,],
    "o": [smalltalk_rule17,],
    "p": [smalltalk_rule17,],
    "q": [smalltalk_rule17,],
    "r": [smalltalk_rule17,],
    "s": [smalltalk_rule17,],
    "t": [smalltalk_rule17,],
    "u": [smalltalk_rule17,],
    "v": [smalltalk_rule17,],
    "w": [smalltalk_rule17,],
    "x": [smalltalk_rule17,],
    "y": [smalltalk_rule17,],
    "z": [smalltalk_rule17,],
}

# x.rulesDictDict for smalltalk mode.
rulesDictDict = {
    "smalltalk_main": rulesDict1,
}

# Import dict for smalltalk mode.
importDict = {}
