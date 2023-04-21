# Leo colorizer control file for objective_c mode.
# This file is in the public domain.

# Properties for objective_c mode.
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

# Attributes dict for objective_c_main ruleset.
objective_c_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for objective_c mode.
attributesDictDict = {
    "objective_c_main": objective_c_main_attributes_dict,
}

# Keywords dict for objective_c_main ruleset.
objective_c_main_keywords_dict = {
    "@class": "keyword1",
    "@defs": "keyword1",
    "@end": "keyword1",
    "@endcode": "keyword1",
    "@implementation": "keyword1",
    "@interface": "keyword1",
    "@private": "keyword1",
    "@protected": "keyword1",
    "@protocol": "keyword1",
    "@public": "keyword1",
    "@selector": "keyword1",
    "BOOL": "keyword3",
    "Class": "keyword3",
    "FALSE": "literal2",
    "IMP": "keyword3",
    "NIl": "literal2",
    "NO": "literal2",
    "NULL": "literal2",
    "SEL": "keyword3",
    "TRUE": "literal2",
    "YES": "literal2",
    "asm": "keyword1",
    "auto": "keyword1",
    "break": "keyword1",
    "bycopy": "keyword1",
    "byref": "keyword1",
    "case": "keyword1",
    "char": "keyword3",
    "const": "keyword3",
    "continue": "keyword1",
    "default": "keyword1",
    "do": "keyword1",
    "double": "keyword3",
    "else": "keyword1",
    "enum": "keyword3",
    "extern": "keyword1",
    "false": "literal2",
    "float": "keyword3",
    "for": "keyword1",
    "goto": "keyword1",
    "id": "keyword3",
    "if": "keyword1",
    "in": "keyword1",
    "inline": "keyword1",
    "inout": "keyword1",
    "int": "keyword3",
    "long": "keyword3",
    "nil": "literal2",
    "oneway": "keyword1",
    "out": "keyword1",
    "register": "keyword1",
    "return": "keyword1",
    "self": "keyword1",
    "short": "keyword3",
    "signed": "keyword3",
    "sizeof": "keyword1",
    "static": "keyword1",
    "struct": "keyword3",
    "super": "keyword1",
    "switch": "keyword1",
    "true": "literal2",
    "typedef": "keyword3",
    "union": "keyword3",
    "unsigned": "keyword3",
    "void": "keyword3",
    "volatile": "keyword1",
    "while": "keyword1",
}

# Dictionary of keywords dictionaries for objective_c mode.
keywordsDictDict = {
    "objective_c_main": objective_c_main_keywords_dict,
}

# Rules for objective_c_main ruleset.

def objective_c_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="doxygen::doxygen")

def objective_c_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/*!", end="*/",
          delegate="doxygen::doxygen")

def objective_c_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def objective_c_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def objective_c_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def objective_c_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="@\"", end="\"",
          no_line_break=True)

def objective_c_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="##")

def objective_c_rule7(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#",
          delegate="c::cpp")

def objective_c_rule8(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def objective_c_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def objective_c_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def objective_c_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def objective_c_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def objective_c_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def objective_c_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def objective_c_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def objective_c_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def objective_c_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def objective_c_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def objective_c_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def objective_c_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def objective_c_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def objective_c_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def objective_c_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def objective_c_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def objective_c_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def objective_c_rule26(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def objective_c_rule27(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def objective_c_rule28(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for objective_c_main ruleset.
rulesDict1 = {
    "!": [objective_c_rule10,],
    "\"": [objective_c_rule3,],
    "#": [objective_c_rule6, objective_c_rule7,],
    "%": [objective_c_rule19,],
    "&": [objective_c_rule20,],
    "'": [objective_c_rule4,],
    "(": [objective_c_rule27,],
    "*": [objective_c_rule16,],
    "+": [objective_c_rule13,],
    "-": [objective_c_rule14,],
    "/": [objective_c_rule0, objective_c_rule1, objective_c_rule2, objective_c_rule8, objective_c_rule15,],
    "0": [objective_c_rule28,],
    "1": [objective_c_rule28,],
    "2": [objective_c_rule28,],
    "3": [objective_c_rule28,],
    "4": [objective_c_rule28,],
    "5": [objective_c_rule28,],
    "6": [objective_c_rule28,],
    "7": [objective_c_rule28,],
    "8": [objective_c_rule28,],
    "9": [objective_c_rule28,],
    ":": [objective_c_rule26,],
    "<": [objective_c_rule12, objective_c_rule18,],
    "=": [objective_c_rule9,],
    ">": [objective_c_rule11, objective_c_rule17,],
    "@": [objective_c_rule5, objective_c_rule28,],
    "A": [objective_c_rule28,],
    "B": [objective_c_rule28,],
    "C": [objective_c_rule28,],
    "D": [objective_c_rule28,],
    "E": [objective_c_rule28,],
    "F": [objective_c_rule28,],
    "G": [objective_c_rule28,],
    "H": [objective_c_rule28,],
    "I": [objective_c_rule28,],
    "J": [objective_c_rule28,],
    "K": [objective_c_rule28,],
    "L": [objective_c_rule28,],
    "M": [objective_c_rule28,],
    "N": [objective_c_rule28,],
    "O": [objective_c_rule28,],
    "P": [objective_c_rule28,],
    "Q": [objective_c_rule28,],
    "R": [objective_c_rule28,],
    "S": [objective_c_rule28,],
    "T": [objective_c_rule28,],
    "U": [objective_c_rule28,],
    "V": [objective_c_rule28,],
    "W": [objective_c_rule28,],
    "X": [objective_c_rule28,],
    "Y": [objective_c_rule28,],
    "Z": [objective_c_rule28,],
    "^": [objective_c_rule22,],
    "a": [objective_c_rule28,],
    "b": [objective_c_rule28,],
    "c": [objective_c_rule28,],
    "d": [objective_c_rule28,],
    "e": [objective_c_rule28,],
    "f": [objective_c_rule28,],
    "g": [objective_c_rule28,],
    "h": [objective_c_rule28,],
    "i": [objective_c_rule28,],
    "j": [objective_c_rule28,],
    "k": [objective_c_rule28,],
    "l": [objective_c_rule28,],
    "m": [objective_c_rule28,],
    "n": [objective_c_rule28,],
    "o": [objective_c_rule28,],
    "p": [objective_c_rule28,],
    "q": [objective_c_rule28,],
    "r": [objective_c_rule28,],
    "s": [objective_c_rule28,],
    "t": [objective_c_rule28,],
    "u": [objective_c_rule28,],
    "v": [objective_c_rule28,],
    "w": [objective_c_rule28,],
    "x": [objective_c_rule28,],
    "y": [objective_c_rule28,],
    "z": [objective_c_rule28,],
    "{": [objective_c_rule25,],
    "|": [objective_c_rule21,],
    "}": [objective_c_rule24,],
    "~": [objective_c_rule23,],
}

# x.rulesDictDict for objective_c mode.
rulesDictDict = {
    "objective_c_main": rulesDict1,
}

# Import dict for objective_c mode.
importDict = {}
