# Leo colorizer control file for awk mode.
# This file is in the public domain.

# Properties for awk mode.
properties = {
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "#",
    "lineUpClosingBracket": "true",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for awk_main ruleset.
awk_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for awk mode.
attributesDictDict = {
    "awk_main": awk_main_attributes_dict,
}

# Keywords dict for awk_main ruleset.
awk_main_keywords_dict = {
    "$0": "keyword3",
    "ARGC": "keyword3",
    "ARGIND": "keyword3",
    "ARGV": "keyword3",
    "BEGIN": "keyword3",
    "CONVFMT": "keyword3",
    "END": "keyword3",
    "ENVIRON": "keyword3",
    "ERRNO": "keyword3",
    "FIELDSWIDTH": "keyword3",
    "FILENAME": "keyword3",
    "FNR": "keyword3",
    "FS": "keyword3",
    "IGNORECASE": "keyword3",
    "NF": "keyword3",
    "NR": "keyword3",
    "OFMT": "keyword3",
    "OFS": "keyword3",
    "ORS": "keyword3",
    "RLENGTH": "keyword3",
    "RS": "keyword3",
    "RSTART": "keyword3",
    "RT": "keyword3",
    "SUBSEP": "keyword3",
    "atan2": "keyword2",
    "break": "keyword1",
    "close": "keyword1",
    "continue": "keyword1",
    "cos": "keyword2",
    "delete": "keyword1",
    "do": "keyword1",
    "else": "keyword1",
    "exit": "keyword1",
    "exp": "keyword2",
    "fflush": "keyword1",
    "for": "keyword1",
    "function": "keyword1",
    "gensub": "keyword2",
    "getline": "keyword2",
    "gsub": "keyword2",
    "huge": "keyword1",
    "if": "keyword1",
    "in": "keyword1",
    "index": "keyword2",
    "int": "keyword2",
    "length": "keyword2",
    "log": "keyword2",
    "match": "keyword2",
    "next": "keyword1",
    "nextfile": "keyword1",
    "print": "keyword1",
    "printf": "keyword1",
    "rand": "keyword2",
    "return": "keyword1",
    "sin": "keyword2",
    "split": "keyword2",
    "sprintf": "keyword2",
    "sqrt": "keyword2",
    "srand": "keyword2",
    "sub": "keyword2",
    "substr": "keyword2",
    "system": "keyword2",
    "tolower": "keyword2",
    "toupper": "keyword2",
    "while": "keyword1",
}

# Dictionary of keywords dictionaries for awk mode.
keywordsDictDict = {
    "awk_main": awk_main_keywords_dict,
}

# Rules for awk_main ruleset.

def awk_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def awk_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def awk_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def awk_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def awk_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def awk_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def awk_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def awk_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def awk_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def awk_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def awk_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def awk_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def awk_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def awk_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def awk_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def awk_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def awk_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def awk_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def awk_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def awk_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def awk_rule20(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def awk_rule21(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for awk_main ruleset.
rulesDict1 = {
    "!": [awk_rule4,],
    "\"": [awk_rule0,],
    "#": [awk_rule2,],
    "$": [awk_rule21,],
    "%": [awk_rule13,],
    "&": [awk_rule14,],
    "'": [awk_rule1,],
    "*": [awk_rule10,],
    "+": [awk_rule7,],
    "-": [awk_rule8,],
    "/": [awk_rule9,],
    "0": [awk_rule21,],
    "1": [awk_rule21,],
    "2": [awk_rule21,],
    "3": [awk_rule21,],
    "4": [awk_rule21,],
    "5": [awk_rule21,],
    "6": [awk_rule21,],
    "7": [awk_rule21,],
    "8": [awk_rule21,],
    "9": [awk_rule21,],
    ":": [awk_rule20,],
    "<": [awk_rule6, awk_rule12,],
    "=": [awk_rule3,],
    ">": [awk_rule5, awk_rule11,],
    "@": [awk_rule21,],
    "A": [awk_rule21,],
    "B": [awk_rule21,],
    "C": [awk_rule21,],
    "D": [awk_rule21,],
    "E": [awk_rule21,],
    "F": [awk_rule21,],
    "G": [awk_rule21,],
    "H": [awk_rule21,],
    "I": [awk_rule21,],
    "J": [awk_rule21,],
    "K": [awk_rule21,],
    "L": [awk_rule21,],
    "M": [awk_rule21,],
    "N": [awk_rule21,],
    "O": [awk_rule21,],
    "P": [awk_rule21,],
    "Q": [awk_rule21,],
    "R": [awk_rule21,],
    "S": [awk_rule21,],
    "T": [awk_rule21,],
    "U": [awk_rule21,],
    "V": [awk_rule21,],
    "W": [awk_rule21,],
    "X": [awk_rule21,],
    "Y": [awk_rule21,],
    "Z": [awk_rule21,],
    "^": [awk_rule16,],
    "a": [awk_rule21,],
    "b": [awk_rule21,],
    "c": [awk_rule21,],
    "d": [awk_rule21,],
    "e": [awk_rule21,],
    "f": [awk_rule21,],
    "g": [awk_rule21,],
    "h": [awk_rule21,],
    "i": [awk_rule21,],
    "j": [awk_rule21,],
    "k": [awk_rule21,],
    "l": [awk_rule21,],
    "m": [awk_rule21,],
    "n": [awk_rule21,],
    "o": [awk_rule21,],
    "p": [awk_rule21,],
    "q": [awk_rule21,],
    "r": [awk_rule21,],
    "s": [awk_rule21,],
    "t": [awk_rule21,],
    "u": [awk_rule21,],
    "v": [awk_rule21,],
    "w": [awk_rule21,],
    "x": [awk_rule21,],
    "y": [awk_rule21,],
    "z": [awk_rule21,],
    "{": [awk_rule19,],
    "|": [awk_rule15,],
    "}": [awk_rule18,],
    "~": [awk_rule17,],
}

# x.rulesDictDict for awk mode.
rulesDictDict = {
    "awk_main": rulesDict1,
}

# Import dict for awk mode.
importDict = {}
