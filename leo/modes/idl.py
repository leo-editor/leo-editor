# Leo colorizer control file for idl mode.
# This file is in the public domain.

# Properties for idl mode.
properties = {
    "boxComment": "*",
    "commentEnd": "*/",
    "commentStart": "/*",
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
}

# Attributes dict for idl_main ruleset.
idl_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for idl mode.
attributesDictDict = {
    "idl_main": idl_main_attributes_dict,
}

# Keywords dict for idl_main ruleset.
idl_main_keywords_dict = {
    "FALSE": "literal2",
    "Object": "keyword3",
    "TRUE": "literal2",
    "any": "keyword3",
    "attribute": "keyword1",
    "boolean": "keyword3",
    "case": "keyword1",
    "char": "keyword3",
    "const": "keyword1",
    "context": "keyword1",
    "default": "keyword1",
    "double": "keyword3",
    "enum": "keyword3",
    "exception": "keyword1",
    "fixed": "keyword1",
    "float": "keyword3",
    "in": "keyword1",
    "inout": "keyword1",
    "interface": "keyword1",
    "long": "keyword3",
    "module": "keyword1",
    "octet": "keyword3",
    "oneway": "keyword1",
    "out": "keyword1",
    "raises": "keyword1",
    "readonly": "keyword1",
    "sequence": "keyword3",
    "short": "keyword3",
    "string": "keyword3",
    "struct": "keyword3",
    "switch": "keyword1",
    "typedef": "keyword3",
    "union": "keyword3",
    "unsigned": "keyword3",
    "void": "keyword3",
    "wchar": "keyword3",
    "wstring": "keyword3",
}

# Dictionary of keywords dictionaries for idl mode.
keywordsDictDict = {
    "idl_main": idl_main_keywords_dict,
}

# Rules for idl_main ruleset.

def idl_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def idl_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def idl_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def idl_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def idl_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def idl_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def idl_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def idl_rule7(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def idl_rule8(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for idl_main ruleset.
rulesDict1 = {
    "\"": [idl_rule1,],
    "'": [idl_rule2,],
    "(": [idl_rule7,],
    "/": [idl_rule0, idl_rule3,],
    "0": [idl_rule8,],
    "1": [idl_rule8,],
    "2": [idl_rule8,],
    "3": [idl_rule8,],
    "4": [idl_rule8,],
    "5": [idl_rule8,],
    "6": [idl_rule8,],
    "7": [idl_rule8,],
    "8": [idl_rule8,],
    "9": [idl_rule8,],
    ":": [idl_rule6,],
    "@": [idl_rule8,],
    "A": [idl_rule8,],
    "B": [idl_rule8,],
    "C": [idl_rule8,],
    "D": [idl_rule8,],
    "E": [idl_rule8,],
    "F": [idl_rule8,],
    "G": [idl_rule8,],
    "H": [idl_rule8,],
    "I": [idl_rule8,],
    "J": [idl_rule8,],
    "K": [idl_rule8,],
    "L": [idl_rule8,],
    "M": [idl_rule8,],
    "N": [idl_rule8,],
    "O": [idl_rule8,],
    "P": [idl_rule8,],
    "Q": [idl_rule8,],
    "R": [idl_rule8,],
    "S": [idl_rule8,],
    "T": [idl_rule8,],
    "U": [idl_rule8,],
    "V": [idl_rule8,],
    "W": [idl_rule8,],
    "X": [idl_rule8,],
    "Y": [idl_rule8,],
    "Z": [idl_rule8,],
    "a": [idl_rule8,],
    "b": [idl_rule8,],
    "c": [idl_rule8,],
    "d": [idl_rule8,],
    "e": [idl_rule8,],
    "f": [idl_rule8,],
    "g": [idl_rule8,],
    "h": [idl_rule8,],
    "i": [idl_rule8,],
    "j": [idl_rule8,],
    "k": [idl_rule8,],
    "l": [idl_rule8,],
    "m": [idl_rule8,],
    "n": [idl_rule8,],
    "o": [idl_rule8,],
    "p": [idl_rule8,],
    "q": [idl_rule8,],
    "r": [idl_rule8,],
    "s": [idl_rule8,],
    "t": [idl_rule8,],
    "u": [idl_rule8,],
    "v": [idl_rule8,],
    "w": [idl_rule8,],
    "x": [idl_rule8,],
    "y": [idl_rule8,],
    "z": [idl_rule8,],
    "{": [idl_rule5,],
    "}": [idl_rule4,],
}

# x.rulesDictDict for idl mode.
rulesDictDict = {
    "idl_main": rulesDict1,
}

# Import dict for idl mode.
importDict = {}
