# Leo colorizer control file for splus mode.
# This file is in the public domain.

# Properties for splus mode.
properties = {
    "doubleBracketIndent": "false",
    "indentCloseBrackets": "}",
    "indentNextLine": "\\s*(((if|while)\\s*\\(|else\\s*|else\\s+if\\s*\\(|for\\s*\\(.*\\))[^{;]*)",
    "indentOpenBrackets": "{",
    "lineComment": "#",
    "lineUpClosingBracket": "true",
    "wordBreakChars": "_,+-=<>/?^&*",
}

# Attributes dict for splus_main ruleset.
splus_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for splus mode.
attributesDictDict = {
    "splus_main": splus_main_attributes_dict,
}

# Keywords dict for splus_main ruleset.
splus_main_keywords_dict = {
    "F": "literal2",
    "T": "literal2",
    "break": "keyword1",
    "case": "keyword1",
    "continue": "keyword1",
    "default": "keyword1",
    "do": "keyword1",
    "else": "keyword1",
    "for": "keyword1",
    "function": "keyword1",
    "goto": "keyword1",
    "if": "keyword1",
    "return": "keyword1",
    "sizeof": "keyword1",
    "switch": "keyword1",
    "while": "keyword1",
}

# Dictionary of keywords dictionaries for splus mode.
keywordsDictDict = {
    "splus_main": splus_main_keywords_dict,
}

# Rules for splus_main ruleset.

def splus_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def splus_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def splus_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def splus_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def splus_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def splus_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="_")

def splus_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def splus_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def splus_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<-")

def splus_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def splus_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def splus_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def splus_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def splus_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def splus_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def splus_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def splus_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def splus_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def splus_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def splus_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def splus_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def splus_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def splus_rule22(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def splus_rule23(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def splus_rule24(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for splus_main ruleset.
rulesDict1 = {
    "!": [splus_rule4,],
    "\"": [splus_rule0,],
    "#": [splus_rule2,],
    "%": [splus_rule15,],
    "&": [splus_rule16,],
    "'": [splus_rule1,],
    "(": [splus_rule23,],
    "*": [splus_rule12,],
    "+": [splus_rule9,],
    "-": [splus_rule10,],
    "/": [splus_rule11,],
    "0": [splus_rule24,],
    "1": [splus_rule24,],
    "2": [splus_rule24,],
    "3": [splus_rule24,],
    "4": [splus_rule24,],
    "5": [splus_rule24,],
    "6": [splus_rule24,],
    "7": [splus_rule24,],
    "8": [splus_rule24,],
    "9": [splus_rule24,],
    ":": [splus_rule22,],
    "<": [splus_rule7, splus_rule8, splus_rule14,],
    "=": [splus_rule3,],
    ">": [splus_rule6, splus_rule13,],
    "@": [splus_rule24,],
    "A": [splus_rule24,],
    "B": [splus_rule24,],
    "C": [splus_rule24,],
    "D": [splus_rule24,],
    "E": [splus_rule24,],
    "F": [splus_rule24,],
    "G": [splus_rule24,],
    "H": [splus_rule24,],
    "I": [splus_rule24,],
    "J": [splus_rule24,],
    "K": [splus_rule24,],
    "L": [splus_rule24,],
    "M": [splus_rule24,],
    "N": [splus_rule24,],
    "O": [splus_rule24,],
    "P": [splus_rule24,],
    "Q": [splus_rule24,],
    "R": [splus_rule24,],
    "S": [splus_rule24,],
    "T": [splus_rule24,],
    "U": [splus_rule24,],
    "V": [splus_rule24,],
    "W": [splus_rule24,],
    "X": [splus_rule24,],
    "Y": [splus_rule24,],
    "Z": [splus_rule24,],
    "^": [splus_rule18,],
    "_": [splus_rule5,],
    "a": [splus_rule24,],
    "b": [splus_rule24,],
    "c": [splus_rule24,],
    "d": [splus_rule24,],
    "e": [splus_rule24,],
    "f": [splus_rule24,],
    "g": [splus_rule24,],
    "h": [splus_rule24,],
    "i": [splus_rule24,],
    "j": [splus_rule24,],
    "k": [splus_rule24,],
    "l": [splus_rule24,],
    "m": [splus_rule24,],
    "n": [splus_rule24,],
    "o": [splus_rule24,],
    "p": [splus_rule24,],
    "q": [splus_rule24,],
    "r": [splus_rule24,],
    "s": [splus_rule24,],
    "t": [splus_rule24,],
    "u": [splus_rule24,],
    "v": [splus_rule24,],
    "w": [splus_rule24,],
    "x": [splus_rule24,],
    "y": [splus_rule24,],
    "z": [splus_rule24,],
    "{": [splus_rule21,],
    "|": [splus_rule17,],
    "}": [splus_rule20,],
    "~": [splus_rule19,],
}

# x.rulesDictDict for splus mode.
rulesDictDict = {
    "splus_main": rulesDict1,
}

# Import dict for splus mode.
importDict = {}
