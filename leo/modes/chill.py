# Leo colorizer control file for chill mode.
# This file is in the public domain.

# Properties for chill mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
}

# Attributes dict for chill_main ruleset.
chill_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for chill mode.
attributesDictDict = {
    "chill_main": chill_main_attributes_dict,
}

# Keywords dict for chill_main ruleset.
chill_main_keywords_dict = {
    "and": "keyword1",
    "array": "keyword2",
    "begin": "keyword1",
    "bin": "keyword3",
    "bool": "keyword3",
    "case": "keyword1",
    "char": "keyword3",
    "dcl": "keyword2",
    "div": "keyword1",
    "do": "keyword1",
    "eject": "label",
    "else": "keyword1",
    "elsif": "keyword1",
    "end": "keyword1",
    "esac": "keyword1",
    "exit": "keyword1",
    "false": "literal2",
    "fi": "keyword1",
    "for": "keyword1",
    "goto": "keyword1",
    "grant": "keyword2",
    "if": "keyword1",
    "in": "keyword1",
    "int": "keyword3",
    "label": "keyword2",
    "lio_infos": "label",
    "mod": "keyword1",
    "module": "keyword2",
    "module_description_header": "label",
    "msg_xref": "label",
    "newmode": "keyword2",
    "not": "keyword1",
    "null": "literal2",
    "od": "keyword1",
    "of": "keyword1",
    "on": "keyword1",
    "or": "keyword1",
    "out": "keyword1",
    "pack": "keyword2",
    "patch_infos": "label",
    "powerset": "keyword2",
    "proc": "keyword2",
    "ptr": "keyword3",
    "range": "keyword3",
    "ref": "keyword3",
    "result": "keyword1",
    "return": "keyword1",
    "seize": "keyword2",
    "set": "keyword2",
    "struct": "keyword2",
    "swsg_infos": "label",
    "syn": "keyword2",
    "synmode": "keyword2",
    "then": "keyword1",
    "to": "keyword1",
    "true": "literal2",
    "type": "keyword2",
    "until": "keyword1",
    "uses": "keyword1",
    "while": "keyword1",
    "with": "keyword1",
    "xor": "keyword1",
}

# Dictionary of keywords dictionaries for chill mode.
keywordsDictDict = {
    "chill_main": chill_main_keywords_dict,
}

# Rules for chill_main ruleset.

def chill_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="<>", end="<>")

def chill_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def chill_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def chill_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="H'", end=";",
          no_line_break=True)

def chill_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def chill_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def chill_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def chill_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def chill_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def chill_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def chill_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def chill_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def chill_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def chill_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def chill_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def chill_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def chill_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def chill_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def chill_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def chill_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def chill_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/=")

def chill_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def chill_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def chill_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def chill_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def chill_rule25(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for chill_main ruleset.
rulesDict1 = {
    "'": [chill_rule2,],
    "(": [chill_rule5,],
    ")": [chill_rule4,],
    "*": [chill_rule11,],
    "+": [chill_rule8,],
    ",": [chill_rule13,],
    "-": [chill_rule9,],
    ".": [chill_rule12,],
    "/": [chill_rule1, chill_rule10, chill_rule20,],
    "0": [chill_rule25,],
    "1": [chill_rule25,],
    "2": [chill_rule25,],
    "3": [chill_rule25,],
    "4": [chill_rule25,],
    "5": [chill_rule25,],
    "6": [chill_rule25,],
    "7": [chill_rule25,],
    "8": [chill_rule25,],
    "9": [chill_rule25,],
    ":": [chill_rule17, chill_rule18,],
    ";": [chill_rule14,],
    "<": [chill_rule0, chill_rule22, chill_rule24,],
    "=": [chill_rule19,],
    ">": [chill_rule21, chill_rule23,],
    "@": [chill_rule16, chill_rule25,],
    "A": [chill_rule25,],
    "B": [chill_rule25,],
    "C": [chill_rule25,],
    "D": [chill_rule25,],
    "E": [chill_rule25,],
    "F": [chill_rule25,],
    "G": [chill_rule25,],
    "H": [chill_rule3, chill_rule25,],
    "I": [chill_rule25,],
    "J": [chill_rule25,],
    "K": [chill_rule25,],
    "L": [chill_rule25,],
    "M": [chill_rule25,],
    "N": [chill_rule25,],
    "O": [chill_rule25,],
    "P": [chill_rule25,],
    "Q": [chill_rule25,],
    "R": [chill_rule25,],
    "S": [chill_rule25,],
    "T": [chill_rule25,],
    "U": [chill_rule25,],
    "V": [chill_rule25,],
    "W": [chill_rule25,],
    "X": [chill_rule25,],
    "Y": [chill_rule25,],
    "Z": [chill_rule25,],
    "[": [chill_rule7,],
    "]": [chill_rule6,],
    "^": [chill_rule15,],
    "_": [chill_rule25,],
    "a": [chill_rule25,],
    "b": [chill_rule25,],
    "c": [chill_rule25,],
    "d": [chill_rule25,],
    "e": [chill_rule25,],
    "f": [chill_rule25,],
    "g": [chill_rule25,],
    "h": [chill_rule25,],
    "i": [chill_rule25,],
    "j": [chill_rule25,],
    "k": [chill_rule25,],
    "l": [chill_rule25,],
    "m": [chill_rule25,],
    "n": [chill_rule25,],
    "o": [chill_rule25,],
    "p": [chill_rule25,],
    "q": [chill_rule25,],
    "r": [chill_rule25,],
    "s": [chill_rule25,],
    "t": [chill_rule25,],
    "u": [chill_rule25,],
    "v": [chill_rule25,],
    "w": [chill_rule25,],
    "x": [chill_rule25,],
    "y": [chill_rule25,],
    "z": [chill_rule25,],
}

# x.rulesDictDict for chill mode.
rulesDictDict = {
    "chill_main": rulesDict1,
}

# Import dict for chill mode.
importDict = {}
