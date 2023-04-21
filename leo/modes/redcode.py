# Leo colorizer control file for redcode mode.
# This file is in the public domain.

# Properties for redcode mode.
properties = {
    "lineComment": ";",
}

# Attributes dict for redcode_main ruleset.
redcode_main_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for redcode mode.
attributesDictDict = {
    "redcode_main": redcode_main_attributes_dict,
}

# Keywords dict for redcode_main ruleset.
redcode_main_keywords_dict = {
    "add": "keyword1",
    "cmp": "keyword1",
    "coresize": "keyword2",
    "curline": "keyword2",
    "dat": "keyword1",
    "div": "keyword1",
    "djn": "keyword1",
    "end": "keyword2",
    "equ": "keyword2",
    "for": "keyword2",
    "jmn": "keyword1",
    "jmp": "keyword1",
    "jmz": "keyword1",
    "ldp": "keyword1",
    "maxcycles": "keyword2",
    "maxlength": "keyword2",
    "maxprocesses": "keyword2",
    "mindistance": "keyword2",
    "mod": "keyword1",
    "mov": "keyword1",
    "mul": "keyword1",
    "nop": "keyword1",
    "org": "keyword2",
    "pin": "keyword2",
    "pspacesize": "keyword2",
    "rof": "keyword2",
    "rounds": "keyword2",
    "seq": "keyword1",
    "slt": "keyword1",
    "sne": "keyword1",
    "spl": "keyword1",
    "stp": "keyword1",
    "sub": "keyword1",
    "version": "keyword2",
    "warriors": "keyword2",
}

# Dictionary of keywords dictionaries for redcode mode.
keywordsDictDict = {
    "redcode_main": redcode_main_keywords_dict,
}

# Rules for redcode_main ruleset.

def redcode_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq=";redcode")

def redcode_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq=";author")

def redcode_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq=";name")

def redcode_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq=";strategy")

def redcode_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq=";password")

def redcode_rule5(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";")

def redcode_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq=".AB")

def redcode_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq=".BA")

def redcode_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq=".A")

def redcode_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq=".B")

def redcode_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq=".F")

def redcode_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq=".X")

def redcode_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq=".I")

def redcode_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def redcode_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def redcode_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def redcode_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def redcode_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def redcode_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def redcode_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def redcode_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def redcode_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def redcode_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!=")

def redcode_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def redcode_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def redcode_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def redcode_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def redcode_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&&")

def redcode_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="||")

def redcode_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def redcode_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def redcode_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="$")

def redcode_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="@")

def redcode_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="#")

def redcode_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="*")

def redcode_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="{")

def redcode_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="}")

def redcode_rule37(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for redcode_main ruleset.
rulesDict1 = {
    "!": [redcode_rule22, redcode_rule29,],
    "#": [redcode_rule33,],
    "$": [redcode_rule31,],
    "%": [redcode_rule20,],
    "&": [redcode_rule27,],
    "(": [redcode_rule15,],
    ")": [redcode_rule16,],
    "*": [redcode_rule34,],
    "+": [redcode_rule17,],
    ",": [redcode_rule13,],
    "-": [redcode_rule18,],
    ".": [redcode_rule6, redcode_rule7, redcode_rule8, redcode_rule9, redcode_rule10, redcode_rule11, redcode_rule12,],
    "/": [redcode_rule19,],
    "0": [redcode_rule37,],
    "1": [redcode_rule37,],
    "2": [redcode_rule37,],
    "3": [redcode_rule37,],
    "4": [redcode_rule37,],
    "5": [redcode_rule37,],
    "6": [redcode_rule37,],
    "7": [redcode_rule37,],
    "8": [redcode_rule37,],
    "9": [redcode_rule37,],
    ":": [redcode_rule14,],
    ";": [redcode_rule0, redcode_rule1, redcode_rule2, redcode_rule3, redcode_rule4, redcode_rule5,],
    "<": [redcode_rule23, redcode_rule25,],
    "=": [redcode_rule21, redcode_rule30,],
    ">": [redcode_rule24, redcode_rule26,],
    "@": [redcode_rule32, redcode_rule37,],
    "A": [redcode_rule37,],
    "B": [redcode_rule37,],
    "C": [redcode_rule37,],
    "D": [redcode_rule37,],
    "E": [redcode_rule37,],
    "F": [redcode_rule37,],
    "G": [redcode_rule37,],
    "H": [redcode_rule37,],
    "I": [redcode_rule37,],
    "J": [redcode_rule37,],
    "K": [redcode_rule37,],
    "L": [redcode_rule37,],
    "M": [redcode_rule37,],
    "N": [redcode_rule37,],
    "O": [redcode_rule37,],
    "P": [redcode_rule37,],
    "Q": [redcode_rule37,],
    "R": [redcode_rule37,],
    "S": [redcode_rule37,],
    "T": [redcode_rule37,],
    "U": [redcode_rule37,],
    "V": [redcode_rule37,],
    "W": [redcode_rule37,],
    "X": [redcode_rule37,],
    "Y": [redcode_rule37,],
    "Z": [redcode_rule37,],
    "a": [redcode_rule37,],
    "b": [redcode_rule37,],
    "c": [redcode_rule37,],
    "d": [redcode_rule37,],
    "e": [redcode_rule37,],
    "f": [redcode_rule37,],
    "g": [redcode_rule37,],
    "h": [redcode_rule37,],
    "i": [redcode_rule37,],
    "j": [redcode_rule37,],
    "k": [redcode_rule37,],
    "l": [redcode_rule37,],
    "m": [redcode_rule37,],
    "n": [redcode_rule37,],
    "o": [redcode_rule37,],
    "p": [redcode_rule37,],
    "q": [redcode_rule37,],
    "r": [redcode_rule37,],
    "s": [redcode_rule37,],
    "t": [redcode_rule37,],
    "u": [redcode_rule37,],
    "v": [redcode_rule37,],
    "w": [redcode_rule37,],
    "x": [redcode_rule37,],
    "y": [redcode_rule37,],
    "z": [redcode_rule37,],
    "{": [redcode_rule35,],
    "|": [redcode_rule28,],
    "}": [redcode_rule36,],
}

# x.rulesDictDict for redcode mode.
rulesDictDict = {
    "redcode_main": rulesDict1,
}

# Import dict for redcode mode.
importDict = {}
