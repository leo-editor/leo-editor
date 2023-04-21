# Leo colorizer control file for ssharp mode.
# This file is in the public domain.

# Properties for ssharp mode.
properties = {
    "commentEnd": "\"",
    "commentStart": "\"",
    "indentCloseBrackets": "]",
    "indentOpenBrackets": "[",
    "lineComment": "#",
    "lineUpClosingBracket": "true",
}

# Attributes dict for ssharp_main ruleset.
ssharp_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for ssharp mode.
attributesDictDict = {
    "ssharp_main": ssharp_main_attributes_dict,
}

# Keywords dict for ssharp_main ruleset.
ssharp_main_keywords_dict = {
    "?": "keyword2",
    "Application": "literal3",
    "Array": "literal2",
    "Boolean": "literal2",
    "Category": "literal3",
    "Character": "literal2",
    "Class": "literal3",
    "Compiler": "literal3",
    "Date": "literal2",
    "EntryPoint": "literal3",
    "Enum": "literal3",
    "Eval": "literal3",
    "Exception": "literal3",
    "False": "literal2",
    "Function": "literal3",
    "IconResource": "literal3",
    "Integer": "literal2",
    "Interface": "literal3",
    "Literal": "literal3",
    "Method": "literal3",
    "Mixin": "literal3",
    "Module": "literal3",
    "Namespace": "literal3",
    "Object": "literal2",
    "Project": "literal3",
    "Reference": "literal3",
    "Require": "literal3",
    "Resource": "literal3",
    "Signal": "literal3",
    "Smalltalk": "literal2",
    "Specifications": "literal3",
    "String": "literal2",
    "Struct": "literal3",
    "Subsystem": "literal3",
    "Symbol": "literal2",
    "Time": "literal2",
    "Transcript": "literal2",
    "True": "literal2",
    "Warning": "literal3",
    "blockSelf": "keyword2",
    "disable": "keyword1",
    "enable": "keyword1",
    "false": "keyword2",
    "isNil": "keyword4",
    "nil": "keyword2",
    "no": "keyword1",
    "not": "keyword4",
    "off": "keyword1",
    "on": "keyword1",
    "scheduler": "keyword2",
    "self": "keyword2",
    "sender": "keyword2",
    "senderMethod": "keyword2",
    "super": "keyword2",
    "thread": "keyword2",
    "true": "keyword2",
    "yes": "keyword1",
}

# Dictionary of keywords dictionaries for ssharp mode.
keywordsDictDict = {
    "ssharp_main": ssharp_main_keywords_dict,
}

# Rules for ssharp_main ruleset.

def ssharp_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def ssharp_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment3", seq="#")

def ssharp_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="\"\"")

def ssharp_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="\"", end="\"")

def ssharp_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="? ", end="? ")

def ssharp_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def ssharp_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def ssharp_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def ssharp_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def ssharp_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def ssharp_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="_")

def ssharp_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def ssharp_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def ssharp_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def ssharp_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def ssharp_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def ssharp_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def ssharp_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def ssharp_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def ssharp_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def ssharp_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="//")

def ssharp_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\\")

def ssharp_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def ssharp_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="**")

def ssharp_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="#")

def ssharp_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def ssharp_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^^")

def ssharp_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def ssharp_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def ssharp_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="->")

def ssharp_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&&")

def ssharp_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="||")

def ssharp_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^|")

def ssharp_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!=")

def ssharp_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~=")

def ssharp_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!==")

def ssharp_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~~")

def ssharp_rule37(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="keyword3", pattern=":",
          exclude_match=True)

def ssharp_rule38(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="label", pattern="#",
          exclude_match=True)

def ssharp_rule39(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="$",
          exclude_match=True)

def ssharp_rule40(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for ssharp_main ruleset.
rulesDict1 = {
    "!": [ssharp_rule33, ssharp_rule35,],
    "\"": [ssharp_rule2, ssharp_rule3,],
    "#": [ssharp_rule1, ssharp_rule24, ssharp_rule38,],
    "$": [ssharp_rule39,],
    "&": [ssharp_rule30,],
    "'": [ssharp_rule0,],
    "(": [ssharp_rule5,],
    ")": [ssharp_rule6,],
    "*": [ssharp_rule22, ssharp_rule23,],
    "+": [ssharp_rule17,],
    "-": [ssharp_rule18, ssharp_rule29,],
    ".": [ssharp_rule28,],
    "/": [ssharp_rule19, ssharp_rule20,],
    "0": [ssharp_rule40,],
    "1": [ssharp_rule40,],
    "2": [ssharp_rule40,],
    "3": [ssharp_rule40,],
    "4": [ssharp_rule40,],
    "5": [ssharp_rule40,],
    "6": [ssharp_rule40,],
    "7": [ssharp_rule40,],
    "8": [ssharp_rule40,],
    "9": [ssharp_rule40,],
    ":": [ssharp_rule9, ssharp_rule37,],
    ";": [ssharp_rule27,],
    "<": [ssharp_rule14, ssharp_rule16,],
    "=": [ssharp_rule11, ssharp_rule12,],
    ">": [ssharp_rule13, ssharp_rule15,],
    "?": [ssharp_rule4, ssharp_rule40,],
    "@": [ssharp_rule40,],
    "A": [ssharp_rule40,],
    "B": [ssharp_rule40,],
    "C": [ssharp_rule40,],
    "D": [ssharp_rule40,],
    "E": [ssharp_rule40,],
    "F": [ssharp_rule40,],
    "G": [ssharp_rule40,],
    "H": [ssharp_rule40,],
    "I": [ssharp_rule40,],
    "J": [ssharp_rule40,],
    "K": [ssharp_rule40,],
    "L": [ssharp_rule40,],
    "M": [ssharp_rule40,],
    "N": [ssharp_rule40,],
    "O": [ssharp_rule40,],
    "P": [ssharp_rule40,],
    "Q": [ssharp_rule40,],
    "R": [ssharp_rule40,],
    "S": [ssharp_rule40,],
    "T": [ssharp_rule40,],
    "U": [ssharp_rule40,],
    "V": [ssharp_rule40,],
    "W": [ssharp_rule40,],
    "X": [ssharp_rule40,],
    "Y": [ssharp_rule40,],
    "Z": [ssharp_rule40,],
    "\\": [ssharp_rule21,],
    "^": [ssharp_rule25, ssharp_rule26, ssharp_rule32,],
    "_": [ssharp_rule10,],
    "a": [ssharp_rule40,],
    "b": [ssharp_rule40,],
    "c": [ssharp_rule40,],
    "d": [ssharp_rule40,],
    "e": [ssharp_rule40,],
    "f": [ssharp_rule40,],
    "g": [ssharp_rule40,],
    "h": [ssharp_rule40,],
    "i": [ssharp_rule40,],
    "j": [ssharp_rule40,],
    "k": [ssharp_rule40,],
    "l": [ssharp_rule40,],
    "m": [ssharp_rule40,],
    "n": [ssharp_rule40,],
    "o": [ssharp_rule40,],
    "p": [ssharp_rule40,],
    "q": [ssharp_rule40,],
    "r": [ssharp_rule40,],
    "s": [ssharp_rule40,],
    "t": [ssharp_rule40,],
    "u": [ssharp_rule40,],
    "v": [ssharp_rule40,],
    "w": [ssharp_rule40,],
    "x": [ssharp_rule40,],
    "y": [ssharp_rule40,],
    "z": [ssharp_rule40,],
    "{": [ssharp_rule7,],
    "|": [ssharp_rule31,],
    "}": [ssharp_rule8,],
    "~": [ssharp_rule34, ssharp_rule36,],
}

# x.rulesDictDict for ssharp mode.
rulesDictDict = {
    "ssharp_main": rulesDict1,
}

# Import dict for ssharp mode.
importDict = {}
