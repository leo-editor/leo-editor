# Leo colorizer control file for b mode.
# This file is in the public domain.

# Properties for b mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "indentNextLine": "\\s*(((ANY|ASSERT|CASE|CHOICE|IF|LET|PRE|SELECT|VAR|WHILE|WHEN)\\s*\\(|ELSE|ELSEIF|EITHER|OR|VARIANT|INVARIANT)[^;]*|for\\s*\\(.*)",
    "lineComment": "//",
}

# Attributes dict for b_main ruleset.
b_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for b mode.
attributesDictDict = {
    "b_main": b_main_attributes_dict,
}

# Keywords dict for b_main ruleset.
b_main_keywords_dict = {
    "ABSTRACT_CONSTANTS": "keyword2",
    "ABSTRACT_VARIABLES": "keyword2",
    "ANY": "keyword2",
    "ASSERT": "keyword2",
    "ASSERTIONS": "keyword2",
    "BE": "keyword2",
    "BEGIN": "keyword2",
    "CASE": "keyword2",
    "CHOICE": "keyword2",
    "CONCRETE_CONSTANTS": "keyword2",
    "CONCRETE_VARIABLES": "keyword2",
    "CONSTANTS": "keyword2",
    "CONSTRAINTS": "keyword2",
    "DEFINITIONS": "keyword2",
    "DO": "keyword2",
    "EITHER": "keyword2",
    "ELSE": "keyword2",
    "ELSIF": "keyword2",
    "END": "keyword2",
    "EXTENDS": "keyword2",
    "FIN": "keyword3",
    "FIN1": "keyword3",
    "IF": "keyword2",
    "IMPLEMENTATION": "keyword2",
    "IMPORTS": "keyword2",
    "IN": "keyword2",
    "INCLUDES": "keyword2",
    "INITIALISATION": "keyword2",
    "INT": "keyword3",
    "INTEGER": "keyword3",
    "INTER": "keyword3",
    "INVARIANT": "keyword2",
    "LET": "keyword2",
    "LOCAL_OPERATIONS": "keyword2",
    "MACHINE": "keyword2",
    "MAXINT": "keyword3",
    "MININT": "keyword3",
    "NAT": "keyword3",
    "NAT1": "keyword3",
    "NATURAL": "keyword3",
    "NATURAL1": "keyword3",
    "OF": "keyword2",
    "OPERATIONS": "keyword2",
    "OR": "keyword2",
    "PI": "keyword3",
    "POW": "keyword3",
    "POW1": "keyword3",
    "PRE": "keyword2",
    "PROMOTES": "keyword2",
    "PROPERTIES": "keyword2",
    "REFINEMENT": "keyword2",
    "REFINES": "keyword2",
    "SEES": "keyword2",
    "SELECT": "keyword2",
    "SETS": "keyword2",
    "SIGMA": "keyword3",
    "THEN": "keyword2",
    "UNION": "keyword3",
    "USES": "keyword2",
    "VALUES": "keyword2",
    "VAR": "keyword2",
    "VARIABLES": "keyword2",
    "VARIANT": "keyword2",
    "WHEN": "keyword2",
    "WHERE": "keyword2",
    "WHILE": "keyword2",
    "arity": "function",
    "bin": "function",
    "bool": "function",
    "btree": "function",
    "card": "function",
    "closure": "function",
    "closure1": "function",
    "conc": "function",
    "const": "function",
    "dom": "function",
    "father": "function",
    "first": "function",
    "fnc": "function",
    "front": "function",
    "id": "function",
    "infix": "function",
    "inter": "function",
    "iseq": "function",
    "iseq1": "function",
    "iterate": "function",
    "last": "function",
    "left": "function",
    "max": "function",
    "min": "function",
    "mirror": "function",
    "mod": "function",
    "not": "function",
    "or": "function",
    "perm": "function",
    "postfix": "function",
    "pred": "function",
    "prefix": "function",
    "prj1": "function",
    "prj2": "function",
    "ran": "function",
    "rank": "function",
    "rec": "function",
    "rel": "function",
    "rev": "function",
    "right": "function",
    "r~": "function",
    "seq": "function",
    "seq1": "function",
    "size": "function",
    "sizet": "function",
    "skip": "function",
    "son": "function",
    "sons": "function",
    "struct": "function",
    "subtree": "function",
    "succ": "function",
    "tail": "function",
    "top": "function",
    "tree": "function",
    "union": "function",
}

# Dictionary of keywords dictionaries for b mode.
keywordsDictDict = {
    "b_main": b_main_keywords_dict,
}

# Rules for b_main ruleset.

def b_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/*?", end="?*/")

def b_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def b_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def b_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def b_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def b_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def b_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="#")

def b_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="$0")

def b_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def b_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def b_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def b_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def b_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def b_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def b_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def b_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def b_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def b_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def b_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def b_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def b_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def b_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def b_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def b_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def b_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def b_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def b_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def b_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def b_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def b_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def b_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def b_rule31(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for b_main ruleset.
rulesDict1 = {
    "!": [b_rule5,],
    "\"": [b_rule2,],
    "#": [b_rule6,],
    "$": [b_rule7,],
    "%": [b_rule8,],
    "&": [b_rule10,],
    "'": [b_rule3,],
    "(": [b_rule25,],
    ")": [b_rule26,],
    "*": [b_rule13,],
    "+": [b_rule14,],
    ",": [b_rule24,],
    "-": [b_rule21,],
    ".": [b_rule23,],
    "/": [b_rule0, b_rule1, b_rule4, b_rule15,],
    "0": [b_rule31,],
    "1": [b_rule31,],
    "2": [b_rule31,],
    "3": [b_rule31,],
    "4": [b_rule31,],
    "5": [b_rule31,],
    "6": [b_rule31,],
    "7": [b_rule31,],
    "8": [b_rule31,],
    "9": [b_rule31,],
    ":": [b_rule18,],
    ";": [b_rule19,],
    "<": [b_rule12,],
    "=": [b_rule9,],
    ">": [b_rule11,],
    "@": [b_rule31,],
    "A": [b_rule31,],
    "B": [b_rule31,],
    "C": [b_rule31,],
    "D": [b_rule31,],
    "E": [b_rule31,],
    "F": [b_rule31,],
    "G": [b_rule31,],
    "H": [b_rule31,],
    "I": [b_rule31,],
    "J": [b_rule31,],
    "K": [b_rule31,],
    "L": [b_rule31,],
    "M": [b_rule31,],
    "N": [b_rule31,],
    "O": [b_rule31,],
    "P": [b_rule31,],
    "Q": [b_rule31,],
    "R": [b_rule31,],
    "S": [b_rule31,],
    "T": [b_rule31,],
    "U": [b_rule31,],
    "V": [b_rule31,],
    "W": [b_rule31,],
    "X": [b_rule31,],
    "Y": [b_rule31,],
    "Z": [b_rule31,],
    "[": [b_rule30,],
    "\\": [b_rule16,],
    "]": [b_rule29,],
    "^": [b_rule22,],
    "_": [b_rule31,],
    "a": [b_rule31,],
    "b": [b_rule31,],
    "c": [b_rule31,],
    "d": [b_rule31,],
    "e": [b_rule31,],
    "f": [b_rule31,],
    "g": [b_rule31,],
    "h": [b_rule31,],
    "i": [b_rule31,],
    "j": [b_rule31,],
    "k": [b_rule31,],
    "l": [b_rule31,],
    "m": [b_rule31,],
    "n": [b_rule31,],
    "o": [b_rule31,],
    "p": [b_rule31,],
    "q": [b_rule31,],
    "r": [b_rule31,],
    "s": [b_rule31,],
    "t": [b_rule31,],
    "u": [b_rule31,],
    "v": [b_rule31,],
    "w": [b_rule31,],
    "x": [b_rule31,],
    "y": [b_rule31,],
    "z": [b_rule31,],
    "{": [b_rule28,],
    "|": [b_rule20,],
    "}": [b_rule27,],
    "~": [b_rule17, b_rule31,],
}

# x.rulesDictDict for b mode.
rulesDictDict = {
    "b_main": rulesDict1,
}

# Import dict for b mode.
importDict = {}
