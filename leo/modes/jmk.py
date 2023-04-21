# Leo colorizer control file for jmk mode.
# This file is in the public domain.

# Properties for jmk mode.
properties = {
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "#",
    "lineUpClosingBracket": "true",
}

# Attributes dict for jmk_main ruleset.
jmk_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for jmk mode.
attributesDictDict = {
    "jmk_main": jmk_main_attributes_dict,
}

# Keywords dict for jmk_main ruleset.
jmk_main_keywords_dict = {
    "%": "keyword2",
    "<": "keyword2",
    "?": "keyword2",
    "@": "keyword2",
    "cat": "keyword1",
    "copy": "keyword1",
    "create": "keyword1",
    "delall": "keyword1",
    "delete": "keyword1",
    "dirs": "keyword1",
    "else": "keyword1",
    "end": "keyword1",
    "equal": "keyword1",
    "exec": "keyword1",
    "first": "keyword1",
    "forname": "keyword1",
    "function": "keyword1",
    "getprop": "keyword1",
    "glob": "keyword1",
    "if": "keyword1",
    "include": "keyword3",
    "join": "keyword1",
    "load": "keyword1",
    "mkdir": "keyword1",
    "mkdirs": "keyword1",
    "note": "keyword1",
    "patsubst": "keyword1",
    "rename": "keyword1",
    "rest": "keyword1",
    "subst": "keyword1",
    "then": "keyword1",
}

# Dictionary of keywords dictionaries for jmk mode.
keywordsDictDict = {
    "jmk_main": jmk_main_keywords_dict,
}

# Rules for jmk_main ruleset.

def jmk_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def jmk_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def jmk_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def jmk_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def jmk_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def jmk_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def jmk_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def jmk_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def jmk_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def jmk_rule9(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for jmk_main ruleset.
rulesDict1 = {
    "\"": [jmk_rule1,],
    "#": [jmk_rule0,],
    "%": [jmk_rule9,],
    "'": [jmk_rule2,],
    "(": [jmk_rule5,],
    ")": [jmk_rule6,],
    "-": [jmk_rule7,],
    "0": [jmk_rule9,],
    "1": [jmk_rule9,],
    "2": [jmk_rule9,],
    "3": [jmk_rule9,],
    "4": [jmk_rule9,],
    "5": [jmk_rule9,],
    "6": [jmk_rule9,],
    "7": [jmk_rule9,],
    "8": [jmk_rule9,],
    "9": [jmk_rule9,],
    "<": [jmk_rule9,],
    "=": [jmk_rule8,],
    "?": [jmk_rule9,],
    "@": [jmk_rule9,],
    "A": [jmk_rule9,],
    "B": [jmk_rule9,],
    "C": [jmk_rule9,],
    "D": [jmk_rule9,],
    "E": [jmk_rule9,],
    "F": [jmk_rule9,],
    "G": [jmk_rule9,],
    "H": [jmk_rule9,],
    "I": [jmk_rule9,],
    "J": [jmk_rule9,],
    "K": [jmk_rule9,],
    "L": [jmk_rule9,],
    "M": [jmk_rule9,],
    "N": [jmk_rule9,],
    "O": [jmk_rule9,],
    "P": [jmk_rule9,],
    "Q": [jmk_rule9,],
    "R": [jmk_rule9,],
    "S": [jmk_rule9,],
    "T": [jmk_rule9,],
    "U": [jmk_rule9,],
    "V": [jmk_rule9,],
    "W": [jmk_rule9,],
    "X": [jmk_rule9,],
    "Y": [jmk_rule9,],
    "Z": [jmk_rule9,],
    "a": [jmk_rule9,],
    "b": [jmk_rule9,],
    "c": [jmk_rule9,],
    "d": [jmk_rule9,],
    "e": [jmk_rule9,],
    "f": [jmk_rule9,],
    "g": [jmk_rule9,],
    "h": [jmk_rule9,],
    "i": [jmk_rule9,],
    "j": [jmk_rule9,],
    "k": [jmk_rule9,],
    "l": [jmk_rule9,],
    "m": [jmk_rule9,],
    "n": [jmk_rule9,],
    "o": [jmk_rule9,],
    "p": [jmk_rule9,],
    "q": [jmk_rule9,],
    "r": [jmk_rule9,],
    "s": [jmk_rule9,],
    "t": [jmk_rule9,],
    "u": [jmk_rule9,],
    "v": [jmk_rule9,],
    "w": [jmk_rule9,],
    "x": [jmk_rule9,],
    "y": [jmk_rule9,],
    "z": [jmk_rule9,],
    "{": [jmk_rule3,],
    "}": [jmk_rule4,],
}

# x.rulesDictDict for jmk mode.
rulesDictDict = {
    "jmk_main": rulesDict1,
}

# Import dict for jmk mode.
importDict = {}
