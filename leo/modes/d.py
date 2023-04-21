# Leo colorizer control file for d mode.
# This file is in the public domain.

# Properties for d mode.
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

# Attributes dict for d_main ruleset.
d_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[0-9a-fA-F_]+[uUlL]?|[0-9_]+(e[0-9_]*)?[uUlLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for d mode.
attributesDictDict = {
    "d_main": d_main_attributes_dict,
}

# Keywords dict for d_main ruleset.
d_main_keywords_dict = {
    "abstract": "keyword1",
    "alias": "keyword3",
    "align": "keyword4",
    "asm": "keyword2",
    "assert": "keyword2",
    "auto": "keyword3",
    "bit": "keyword3",
    "body": "keyword4",
    "break": "keyword1",
    "byte": "keyword3",
    "case>": "keyword1",
    "cast": "keyword3",
    "catch": "keyword1",
    "cdouble": "keyword3",
    "cent": "keyword3",
    "cfloat": "keyword3",
    "char": "keyword3",
    "class": "keyword3",
    "const": "invalid",
    "continue": "keyword1",
    "creal": "keyword3",
    "dchar": "keyword3",
    "debug": "keyword2",
    "default": "keyword1",
    "delegate": "keyword4",
    "delete": "keyword1",
    "deprecated": "keyword2",
    "do": "keyword1",
    "double": "keyword3",
    "else": "keyword1",
    "enum": "keyword3",
    "export": "keyword2",
    "extern": "keyword2",
    "false": "literal2",
    "final": "keyword1",
    "finally": "keyword1",
    "float": "keyword3",
    "for": "keyword1",
    "foreach": "keyword1",
    "function": "keyword4",
    "goto": "invalid",
    "idouble": "keyword3",
    "if": "keyword1",
    "ifloat": "keyword3",
    "import": "keyword2",
    "in": "invalid",
    "inout": "invalid",
    "int": "keyword3",
    "interface": "keyword2",
    "invariant": "keyword2",
    "ireal": "keyword3",
    "is": "operator",
    "long": "keyword3",
    "module": "keyword4",
    "new": "keyword1",
    "null": "literal2",
    "out": "invalid",
    "override": "keyword4",
    "package": "keyword2",
    "pragma": "keyword2",
    "private": "keyword1",
    "protected": "keyword1",
    "public": "keyword1",
    "real": "keyword3",
    "return": "keyword1",
    "short": "keyword3",
    "static": "keyword1",
    "struct": "keyword3",
    "super": "literal2",
    "switch": "keyword1",
    "synchronized": "keyword1",
    "template": "keyword3",
    "this": "literal2",
    "throw": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "typedef": "keyword3",
    "typeof": "keyword1",
    "ubyte": "keyword3",
    "ucent": "keyword3",
    "uint": "keyword3",
    "ulong": "keyword3",
    "union": "keyword3",
    "unittest": "keyword2",
    "ushort": "keyword3",
    "version": "keyword2",
    "void": "keyword3",
    "volatile": "keyword1",
    "wchar": "keyword3",
    "while": "keyword1",
    "with": "keyword2",
}

# Dictionary of keywords dictionaries for d mode.
keywordsDictDict = {
    "d_main": d_main_keywords_dict,
}

# Rules for d_main ruleset.

def d_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment1", seq="/**/")

def d_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="doxygen::doxygen")

def d_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/*!", end="*/",
          delegate="doxygen::doxygen")

def d_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def d_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def d_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def d_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def d_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def d_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def d_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def d_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def d_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def d_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def d_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def d_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def d_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def d_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def d_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def d_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def d_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def d_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def d_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def d_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def d_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def d_rule24(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def d_rule25(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def d_rule26(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword4", pattern="@")

def d_rule27(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for d_main ruleset.
rulesDict1 = {
    "!": [d_rule8,],
    "\"": [d_rule4,],
    "%": [d_rule17,],
    "&": [d_rule18,],
    "'": [d_rule5,],
    "(": [d_rule25,],
    "*": [d_rule14,],
    "+": [d_rule11,],
    "-": [d_rule12,],
    "/": [d_rule0, d_rule1, d_rule2, d_rule3, d_rule6, d_rule13,],
    "0": [d_rule27,],
    "1": [d_rule27,],
    "2": [d_rule27,],
    "3": [d_rule27,],
    "4": [d_rule27,],
    "5": [d_rule27,],
    "6": [d_rule27,],
    "7": [d_rule27,],
    "8": [d_rule27,],
    "9": [d_rule27,],
    ":": [d_rule24,],
    "<": [d_rule10, d_rule16,],
    "=": [d_rule7,],
    ">": [d_rule9, d_rule15, d_rule27,],
    "@": [d_rule26, d_rule27,],
    "A": [d_rule27,],
    "B": [d_rule27,],
    "C": [d_rule27,],
    "D": [d_rule27,],
    "E": [d_rule27,],
    "F": [d_rule27,],
    "G": [d_rule27,],
    "H": [d_rule27,],
    "I": [d_rule27,],
    "J": [d_rule27,],
    "K": [d_rule27,],
    "L": [d_rule27,],
    "M": [d_rule27,],
    "N": [d_rule27,],
    "O": [d_rule27,],
    "P": [d_rule27,],
    "Q": [d_rule27,],
    "R": [d_rule27,],
    "S": [d_rule27,],
    "T": [d_rule27,],
    "U": [d_rule27,],
    "V": [d_rule27,],
    "W": [d_rule27,],
    "X": [d_rule27,],
    "Y": [d_rule27,],
    "Z": [d_rule27,],
    "^": [d_rule20,],
    "a": [d_rule27,],
    "b": [d_rule27,],
    "c": [d_rule27,],
    "d": [d_rule27,],
    "e": [d_rule27,],
    "f": [d_rule27,],
    "g": [d_rule27,],
    "h": [d_rule27,],
    "i": [d_rule27,],
    "j": [d_rule27,],
    "k": [d_rule27,],
    "l": [d_rule27,],
    "m": [d_rule27,],
    "n": [d_rule27,],
    "o": [d_rule27,],
    "p": [d_rule27,],
    "q": [d_rule27,],
    "r": [d_rule27,],
    "s": [d_rule27,],
    "t": [d_rule27,],
    "u": [d_rule27,],
    "v": [d_rule27,],
    "w": [d_rule27,],
    "x": [d_rule27,],
    "y": [d_rule27,],
    "z": [d_rule27,],
    "{": [d_rule23,],
    "|": [d_rule19,],
    "}": [d_rule22,],
    "~": [d_rule21,],
}

# x.rulesDictDict for d mode.
rulesDictDict = {
    "d_main": rulesDict1,
}

# Import dict for d mode.
importDict = {}
