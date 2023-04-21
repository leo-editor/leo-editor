# Leo colorizer control file for io mode.
# This file is in the public domain.

# Properties for io mode.
properties = {
    "commentStart": "*/",
    "indentCloseBrackets": ")",
    "indentOpenBrackets": "(",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
}

# Attributes dict for io_main ruleset.
io_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for io mode.
attributesDictDict = {
    "io_main": io_main_attributes_dict,
}

# Keywords dict for io_main ruleset.
io_main_keywords_dict = {
    "Block": "keyword1",
    "Buffer": "keyword1",
    "CFunction": "keyword1",
    "Date": "keyword1",
    "Duration": "keyword1",
    "File": "keyword1",
    "Future": "keyword1",
    "LinkedList": "keyword1",
    "List": "keyword1",
    "Map": "keyword1",
    "Message": "keyword1",
    "Nil": "keyword1",
    "Nop": "keyword1",
    "Number": "keyword1",
    "Object": "keyword1",
    "String": "keyword1",
    "WeakLink": "keyword1",
    "block": "keyword1",
    "clone": "keyword3",
    "do": "keyword2",
    "else": "keyword2",
    "foreach": "keyword2",
    "forward": "keyword3",
    "hasSlot": "keyword3",
    "if": "keyword2",
    "method": "keyword1",
    "print": "keyword3",
    "proto": "keyword3",
    "self": "keyword3",
    "setSlot": "keyword3",
    "super": "keyword3",
    "type": "keyword3",
    "while": "keyword2",
    "write": "keyword3",
}

# Dictionary of keywords dictionaries for io mode.
keywordsDictDict = {
    "io_main": io_main_keywords_dict,
}

# Rules for io_main ruleset.

def io_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def io_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="//")

def io_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def io_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"", end="\"")

def io_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"\"\"", end="\"\"\"")

def io_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="`")

def io_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def io_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def io_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@@")

def io_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="$")

def io_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def io_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def io_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def io_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def io_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def io_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def io_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def io_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def io_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def io_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def io_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def io_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def io_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def io_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def io_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def io_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def io_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def io_rule27(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for io_main ruleset.
rulesDict1 = {
    "\"": [io_rule3, io_rule4,],
    "#": [io_rule0,],
    "$": [io_rule9,],
    "%": [io_rule10,],
    "&": [io_rule12,],
    "*": [io_rule13,],
    "+": [io_rule15,],
    "-": [io_rule14,],
    "/": [io_rule1, io_rule2, io_rule16,],
    "0": [io_rule27,],
    "1": [io_rule27,],
    "2": [io_rule27,],
    "3": [io_rule27,],
    "4": [io_rule27,],
    "5": [io_rule27,],
    "6": [io_rule27,],
    "7": [io_rule27,],
    "8": [io_rule27,],
    "9": [io_rule27,],
    "<": [io_rule25,],
    "=": [io_rule17,],
    ">": [io_rule24,],
    "?": [io_rule26,],
    "@": [io_rule7, io_rule8, io_rule27,],
    "A": [io_rule27,],
    "B": [io_rule27,],
    "C": [io_rule27,],
    "D": [io_rule27,],
    "E": [io_rule27,],
    "F": [io_rule27,],
    "G": [io_rule27,],
    "H": [io_rule27,],
    "I": [io_rule27,],
    "J": [io_rule27,],
    "K": [io_rule27,],
    "L": [io_rule27,],
    "M": [io_rule27,],
    "N": [io_rule27,],
    "O": [io_rule27,],
    "P": [io_rule27,],
    "Q": [io_rule27,],
    "R": [io_rule27,],
    "S": [io_rule27,],
    "T": [io_rule27,],
    "U": [io_rule27,],
    "V": [io_rule27,],
    "W": [io_rule27,],
    "X": [io_rule27,],
    "Y": [io_rule27,],
    "Z": [io_rule27,],
    "[": [io_rule20,],
    "\\": [io_rule23,],
    "]": [io_rule21,],
    "^": [io_rule11,],
    "`": [io_rule5,],
    "a": [io_rule27,],
    "b": [io_rule27,],
    "c": [io_rule27,],
    "d": [io_rule27,],
    "e": [io_rule27,],
    "f": [io_rule27,],
    "g": [io_rule27,],
    "h": [io_rule27,],
    "i": [io_rule27,],
    "j": [io_rule27,],
    "k": [io_rule27,],
    "l": [io_rule27,],
    "m": [io_rule27,],
    "n": [io_rule27,],
    "o": [io_rule27,],
    "p": [io_rule27,],
    "q": [io_rule27,],
    "r": [io_rule27,],
    "s": [io_rule27,],
    "t": [io_rule27,],
    "u": [io_rule27,],
    "v": [io_rule27,],
    "w": [io_rule27,],
    "x": [io_rule27,],
    "y": [io_rule27,],
    "z": [io_rule27,],
    "{": [io_rule18,],
    "|": [io_rule22,],
    "}": [io_rule19,],
    "~": [io_rule6,],
}

# x.rulesDictDict for io mode.
rulesDictDict = {
    "io_main": rulesDict1,
}

# Import dict for io mode.
importDict = {}
