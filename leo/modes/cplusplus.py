# Leo colorizer control file for cplusplus mode.
# This file is in the public domain.

# Properties for cplusplus mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "doubleBracketIndent": "false",
    "indentCloseBrackets": "}",
    "indentNextLine": "\\s*(((if|while)\\s*\\(|else\\s*|else\\s+if\\s*\\(|for\\s*\\(.*\\))[^{;]*)",
    "indentOpenBrackets": "{",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for cplusplus_main ruleset.
cplusplus_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for cplusplus mode.
attributesDictDict = {
    "cplusplus_main": cplusplus_main_attributes_dict,
}

# Keywords dict for cplusplus_main ruleset.
cplusplus_main_keywords_dict = {
    "NULL": "literal2",
    "and": "keyword3",
    "and_eq": "keyword3",
    "asm": "keyword2",
    "auto": "keyword1",
    "bitand": "keyword3",
    "bitor": "keyword3",
    "bool": "keyword3",
    "break": "keyword1",
    "case": "keyword1",
    "catch": "keyword1",
    "char": "keyword3",
    "class": "keyword3",
    "compl": "keyword3",
    "const": "keyword1",
    "const_cast": "keyword3",
    "continue": "keyword1",
    "default": "keyword1",
    "delete": "keyword1",
    "do": "keyword1",
    "double": "keyword3",
    "dynamic_cast": "keyword3",
    "else": "keyword1",
    "enum": "keyword3",
    "explicit": "keyword1",
    "export": "keyword2",
    "extern": "keyword2",
    "false": "literal2",
    "float": "keyword3",
    "for": "keyword1",
    "friend": "keyword1",
    "goto": "keyword1",
    "if": "keyword1",
    "inline": "keyword1",
    "int": "keyword3",
    "long": "keyword3",
    "mutable": "keyword3",
    "namespace": "keyword2",
    "new": "keyword1",
    "not": "keyword3",
    "not_eq": "keyword3",
    "operator": "keyword3",
    "or": "keyword3",
    "or_eq": "keyword3",
    "private": "keyword1",
    "protected": "keyword1",
    "public": "keyword1",
    "register": "keyword1",
    "reinterpret_cast": "keyword3",
    "return": "keyword1",
    "short": "keyword3",
    "signed": "keyword3",
    "sizeof": "keyword1",
    "static": "keyword1",
    "static_cast": "keyword3",
    "struct": "keyword3",
    "switch": "keyword1",
    "template": "keyword3",
    "this": "literal2",
    "throw": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "typedef": "keyword3",
    "typeid": "keyword3",
    "typename": "keyword3",
    "union": "keyword3",
    "unsigned": "keyword3",
    "using": "keyword2",
    "virtual": "keyword1",
    "void": "keyword1",
    "volatile": "keyword1",
    "wchar_t": "keyword3",
    "while": "keyword1",
    "xor": "keyword3",
    "xor_eq": "keyword3",
}

# Dictionary of keywords dictionaries for cplusplus mode.
keywordsDictDict = {
    "cplusplus_main": cplusplus_main_keywords_dict,
}

# Rules for cplusplus_main ruleset.

def cplusplus_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="doxygen::doxygen")

def cplusplus_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/*!", end="*/",
          delegate="doxygen::doxygen")

def cplusplus_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def cplusplus_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def cplusplus_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def cplusplus_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="##")

def cplusplus_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#",
          delegate="c::cpp")

def cplusplus_rule7(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def cplusplus_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def cplusplus_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def cplusplus_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def cplusplus_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def cplusplus_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def cplusplus_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def cplusplus_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def cplusplus_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def cplusplus_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def cplusplus_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def cplusplus_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def cplusplus_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def cplusplus_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def cplusplus_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def cplusplus_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def cplusplus_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def cplusplus_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def cplusplus_rule25(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="::")

def cplusplus_rule26(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def cplusplus_rule27(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def cplusplus_rule28(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for cplusplus_main ruleset.
rulesDict1 = {
    "!": [cplusplus_rule9,],
    "\"": [cplusplus_rule3,],
    "#": [cplusplus_rule5, cplusplus_rule6,],
    "%": [cplusplus_rule18,],
    "&": [cplusplus_rule19,],
    "'": [cplusplus_rule4,],
    "(": [cplusplus_rule27,],
    "*": [cplusplus_rule15,],
    "+": [cplusplus_rule12,],
    "-": [cplusplus_rule13,],
    "/": [cplusplus_rule0, cplusplus_rule1, cplusplus_rule2, cplusplus_rule7, cplusplus_rule14,],
    "0": [cplusplus_rule28,],
    "1": [cplusplus_rule28,],
    "2": [cplusplus_rule28,],
    "3": [cplusplus_rule28,],
    "4": [cplusplus_rule28,],
    "5": [cplusplus_rule28,],
    "6": [cplusplus_rule28,],
    "7": [cplusplus_rule28,],
    "8": [cplusplus_rule28,],
    "9": [cplusplus_rule28,],
    ":": [cplusplus_rule25, cplusplus_rule26,],
    "<": [cplusplus_rule11, cplusplus_rule17,],
    "=": [cplusplus_rule8,],
    ">": [cplusplus_rule10, cplusplus_rule16,],
    "@": [cplusplus_rule28,],
    "A": [cplusplus_rule28,],
    "B": [cplusplus_rule28,],
    "C": [cplusplus_rule28,],
    "D": [cplusplus_rule28,],
    "E": [cplusplus_rule28,],
    "F": [cplusplus_rule28,],
    "G": [cplusplus_rule28,],
    "H": [cplusplus_rule28,],
    "I": [cplusplus_rule28,],
    "J": [cplusplus_rule28,],
    "K": [cplusplus_rule28,],
    "L": [cplusplus_rule28,],
    "M": [cplusplus_rule28,],
    "N": [cplusplus_rule28,],
    "O": [cplusplus_rule28,],
    "P": [cplusplus_rule28,],
    "Q": [cplusplus_rule28,],
    "R": [cplusplus_rule28,],
    "S": [cplusplus_rule28,],
    "T": [cplusplus_rule28,],
    "U": [cplusplus_rule28,],
    "V": [cplusplus_rule28,],
    "W": [cplusplus_rule28,],
    "X": [cplusplus_rule28,],
    "Y": [cplusplus_rule28,],
    "Z": [cplusplus_rule28,],
    "^": [cplusplus_rule21,],
    "_": [cplusplus_rule28,],
    "a": [cplusplus_rule28,],
    "b": [cplusplus_rule28,],
    "c": [cplusplus_rule28,],
    "d": [cplusplus_rule28,],
    "e": [cplusplus_rule28,],
    "f": [cplusplus_rule28,],
    "g": [cplusplus_rule28,],
    "h": [cplusplus_rule28,],
    "i": [cplusplus_rule28,],
    "j": [cplusplus_rule28,],
    "k": [cplusplus_rule28,],
    "l": [cplusplus_rule28,],
    "m": [cplusplus_rule28,],
    "n": [cplusplus_rule28,],
    "o": [cplusplus_rule28,],
    "p": [cplusplus_rule28,],
    "q": [cplusplus_rule28,],
    "r": [cplusplus_rule28,],
    "s": [cplusplus_rule28,],
    "t": [cplusplus_rule28,],
    "u": [cplusplus_rule28,],
    "v": [cplusplus_rule28,],
    "w": [cplusplus_rule28,],
    "x": [cplusplus_rule28,],
    "y": [cplusplus_rule28,],
    "z": [cplusplus_rule28,],
    "{": [cplusplus_rule24,],
    "|": [cplusplus_rule20,],
    "}": [cplusplus_rule23,],
    "~": [cplusplus_rule22,],
}

# x.rulesDictDict for cplusplus mode.
rulesDictDict = {
    "cplusplus_main": rulesDict1,
}

# Import dict for cplusplus mode.
importDict = {}
