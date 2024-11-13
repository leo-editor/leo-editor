# Leo colorizer control file for openscad mode.
# This file is in the public domain.

# Properties for openscad mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "//",
}

# Attributes dict for openscad_main ruleset.
openscad_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for openscad mode.
attributesDictDict = {
    "openscad_main": openscad_main_attributes_dict,
}

# Keywords dict for openscad_main ruleset.
openscad_main_keywords_dict = {
    "abs": "keyword4",
    "acos": "keyword4",
    "asin": "keyword4",
    "assign": "keyword1",
    "atan": "keyword4",
    "atan2": "keyword4",
    "ceil": "keyword4",
    "color": "keyword3",
    "cos": "keyword4",
    "cube": "keyword2",
    "cylinder": "keyword2",
    "difference": "keyword1",
    "echo": "keyword1",
    "else": "keyword1",
    "exp": "keyword4",
    "false": "literal2",
    "floor": "keyword4",
    "for": "keyword1",
    "function": "keyword1",
    "hull": "keyword3",
    "if": "keyword1",
    "include": "markup",
    "intersection": "keyword1",
    "intersection_for": "keyword1",
    "len": "keyword4",
    "ln": "keyword4",
    "log": "keyword4",
    "lookup": "keyword4",
    "max": "keyword4",
    "min": "keyword4",
    "minkowski": "keyword3",
    "mirror": "keyword3",
    "module": "keyword1",
    "multmatrix": "keyword3",
    "polyhedron": "keyword2",
    "pow": "keyword4",
    "rands": "keyword4",
    "render": "keyword1",
    "rotate": "keyword3",
    "round": "keyword4",
    "scale": "keyword3",
    "search": "keyword1",
    "sign": "keyword4",
    "sin": "keyword4",
    "sphere": "keyword2",
    "sqrt": "keyword4",
    "str": "keyword4",
    "surface": "keyword2",
    "tan": "keyword4",
    "translate": "keyword3",
    "true": "literal2",
    "union": "keyword1",
    "use": "markup",
}

# Dictionary of keywords dictionaries for openscad mode.
keywordsDictDict = {
    "openscad_main": openscad_main_keywords_dict,
}

# Rules for openscad_main ruleset.

def openscad_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def openscad_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def openscad_rule2(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def openscad_rule3(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=")",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def openscad_rule5(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="}",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule6(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="{",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule7(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule8(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="[",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule9(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule10(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="&&",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule12(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="||",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="!",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule14(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="<",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule15(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="<=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule16(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="==",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule17(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="!=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule18(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=">=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule19(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule20(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="?",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule21(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=":",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule22(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule23(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="-",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule24(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule25(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="/",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule26(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="%",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule27(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="#",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule28(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp="\\$fa\\b",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule29(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp="\\$fs\\b",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule30(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp="\\$fn\\b",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule31(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp="\\$t\\b",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def openscad_rule32(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal4", pattern="$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def openscad_rule33(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for openscad_main ruleset.
rulesDict1 = {
    "!": [openscad_rule13, openscad_rule17,],
    "\"": [openscad_rule1,],
    "#": [openscad_rule27,],
    "$": [openscad_rule28, openscad_rule29, openscad_rule30, openscad_rule31, openscad_rule32,],
    "%": [openscad_rule26,],
    "&": [openscad_rule11,],
    "(": [openscad_rule2,],
    ")": [openscad_rule3,],
    "*": [openscad_rule24,],
    "+": [openscad_rule22,],
    "-": [openscad_rule23,],
    "/": [openscad_rule0, openscad_rule4, openscad_rule25,],
    "0": [openscad_rule33,],
    "1": [openscad_rule33,],
    "2": [openscad_rule33,],
    "3": [openscad_rule33,],
    "4": [openscad_rule33,],
    "5": [openscad_rule33,],
    "6": [openscad_rule33,],
    "7": [openscad_rule33,],
    "8": [openscad_rule33,],
    "9": [openscad_rule33,],
    ":": [openscad_rule21,],
    ";": [openscad_rule10,],
    "<": [openscad_rule14, openscad_rule15,],
    "=": [openscad_rule9, openscad_rule16,],
    ">": [openscad_rule18, openscad_rule19,],
    "?": [openscad_rule20,],
    "@": [openscad_rule33,],
    "A": [openscad_rule33,],
    "B": [openscad_rule33,],
    "C": [openscad_rule33,],
    "D": [openscad_rule33,],
    "E": [openscad_rule33,],
    "F": [openscad_rule33,],
    "G": [openscad_rule33,],
    "H": [openscad_rule33,],
    "I": [openscad_rule33,],
    "J": [openscad_rule33,],
    "K": [openscad_rule33,],
    "L": [openscad_rule33,],
    "M": [openscad_rule33,],
    "N": [openscad_rule33,],
    "O": [openscad_rule33,],
    "P": [openscad_rule33,],
    "Q": [openscad_rule33,],
    "R": [openscad_rule33,],
    "S": [openscad_rule33,],
    "T": [openscad_rule33,],
    "U": [openscad_rule33,],
    "V": [openscad_rule33,],
    "W": [openscad_rule33,],
    "X": [openscad_rule33,],
    "Y": [openscad_rule33,],
    "Z": [openscad_rule33,],
    "[": [openscad_rule8,],
    "]": [openscad_rule7,],
    "_": [openscad_rule33,],
    "a": [openscad_rule33,],
    "b": [openscad_rule33,],
    "c": [openscad_rule33,],
    "d": [openscad_rule33,],
    "e": [openscad_rule33,],
    "f": [openscad_rule33,],
    "g": [openscad_rule33,],
    "h": [openscad_rule33,],
    "i": [openscad_rule33,],
    "j": [openscad_rule33,],
    "k": [openscad_rule33,],
    "l": [openscad_rule33,],
    "m": [openscad_rule33,],
    "n": [openscad_rule33,],
    "o": [openscad_rule33,],
    "p": [openscad_rule33,],
    "q": [openscad_rule33,],
    "r": [openscad_rule33,],
    "s": [openscad_rule33,],
    "t": [openscad_rule33,],
    "u": [openscad_rule33,],
    "v": [openscad_rule33,],
    "w": [openscad_rule33,],
    "x": [openscad_rule33,],
    "y": [openscad_rule33,],
    "z": [openscad_rule33,],
    "{": [openscad_rule6,],
    "|": [openscad_rule12,],
    "}": [openscad_rule5,],
}

# x.rulesDictDict for openscad mode.
rulesDictDict = {
    "openscad_main": rulesDict1,
}

# Import dict for openscad mode.
importDict = {}

