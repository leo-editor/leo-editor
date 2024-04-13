# Leo colorizer control file for aspect_j mode.
# This file is in the public domain.

# Properties for aspect_j mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "doubleBracketIndent": "false",
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "indentPrevLine": "\\s*(((if|while)\\s*\\(|else\\s*|else\\s+if\\s*\\(|for\\s*\\(.*\\))[^{;]*)",
    "lineComment": "//",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for aspect_j_main ruleset.
aspect_j_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x)?[[:xdigit:]]+[lLdDfF]?",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for aspect_j mode.
attributesDictDict = {
    "aspect_j_main": aspect_j_main_attributes_dict,
}

# Keywords dict for aspect_j_main ruleset.
aspect_j_main_keywords_dict = {
    "..": "keyword4",
    "abstract": "keyword1",
    "adviceexecution": "keyword4",
    "after": "keyword4",
    "args": "keyword4",
    "around": "keyword4",
    "aspect": "keyword4",
    "assert": "function",
    "before": "keyword4",
    "boolean": "keyword3",
    "break": "keyword1",
    "byte": "keyword3",
    "call": "keyword4",
    "case": "keyword1",
    "catch": "keyword1",
    "cflow": "keyword4",
    "cflowbelow": "keyword4",
    "char": "keyword3",
    "class": "keyword3",
    "const": "invalid",
    "continue": "keyword1",
    "declare": "keyword4",
    "default": "keyword1",
    "do": "keyword1",
    "double": "keyword3",
    "else": "keyword1",
    "execution": "keyword4",
    "extends": "keyword1",
    "false": "literal2",
    "final": "keyword1",
    "finally": "keyword1",
    "float": "keyword3",
    "for": "keyword1",
    "get": "keyword4",
    "goto": "invalid",
    "handler": "keyword4",
    "if": "keyword1",
    "implements": "keyword1",
    "import": "keyword2",
    "initialization": "keyword4",
    "instanceof": "keyword1",
    "int": "keyword3",
    "interface": "keyword3",
    "issingleton": "keyword4",
    "long": "keyword3",
    "native": "keyword1",
    "new": "keyword1",
    "null": "literal2",
    "package": "keyword2",
    "percflow": "keyword4",
    "pertarget": "keyword4",
    "perthis": "keyword4",
    "pointcut": "keyword4",
    "precedence": "keyword4",
    "preinitialization": "keyword4",
    "private": "keyword1",
    "privileged": "keyword4",
    "proceed": "keyword4",
    "protected": "keyword1",
    "public": "keyword1",
    "return": "keyword1",
    "set": "keyword4",
    "short": "keyword3",
    "static": "keyword1",
    "staticinitialization": "keyword4",
    "strictfp": "keyword1",
    "super": "literal2",
    "switch": "keyword1",
    "synchronized": "keyword1",
    "target": "keyword4",
    "this": "literal2",
    "throw": "keyword1",
    "throws": "keyword1",
    "transient": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "void": "keyword3",
    "volatile": "keyword1",
    "while": "keyword1",
    "within": "keyword4",
    "withincode": "keyword4",
}

# Dictionary of keywords dictionaries for aspect_j mode.
keywordsDictDict = {
    "aspect_j_main": aspect_j_main_keywords_dict,
}

# Rules for aspect_j_main ruleset.

def aspect_j_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment1", seq="/**/")

def aspect_j_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="java::javadoc")

def aspect_j_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def aspect_j_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def aspect_j_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def aspect_j_rule5(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def aspect_j_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def aspect_j_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def aspect_j_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def aspect_j_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def aspect_j_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def aspect_j_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def aspect_j_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def aspect_j_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=".*")

def aspect_j_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def aspect_j_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def aspect_j_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def aspect_j_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def aspect_j_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def aspect_j_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def aspect_j_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def aspect_j_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def aspect_j_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def aspect_j_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def aspect_j_rule24(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def aspect_j_rule25(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def aspect_j_rule26(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for aspect_j_main ruleset.
rulesDict1 = {
    "!": [aspect_j_rule7,],
    "\"": [aspect_j_rule3,],
    "%": [aspect_j_rule17,],
    "&": [aspect_j_rule18,],
    "'": [aspect_j_rule4,],
    "(": [aspect_j_rule25,],
    "*": [aspect_j_rule14,],
    "+": [aspect_j_rule10,],
    "-": [aspect_j_rule11,],
    ".": [aspect_j_rule13, aspect_j_rule26,],
    "/": [aspect_j_rule0, aspect_j_rule1, aspect_j_rule2, aspect_j_rule5, aspect_j_rule12,],
    "0": [aspect_j_rule26,],
    "1": [aspect_j_rule26,],
    "2": [aspect_j_rule26,],
    "3": [aspect_j_rule26,],
    "4": [aspect_j_rule26,],
    "5": [aspect_j_rule26,],
    "6": [aspect_j_rule26,],
    "7": [aspect_j_rule26,],
    "8": [aspect_j_rule26,],
    "9": [aspect_j_rule26,],
    ":": [aspect_j_rule24,],
    "<": [aspect_j_rule9, aspect_j_rule16,],
    "=": [aspect_j_rule6,],
    ">": [aspect_j_rule8, aspect_j_rule15,],
    "@": [aspect_j_rule26,],
    "A": [aspect_j_rule26,],
    "B": [aspect_j_rule26,],
    "C": [aspect_j_rule26,],
    "D": [aspect_j_rule26,],
    "E": [aspect_j_rule26,],
    "F": [aspect_j_rule26,],
    "G": [aspect_j_rule26,],
    "H": [aspect_j_rule26,],
    "I": [aspect_j_rule26,],
    "J": [aspect_j_rule26,],
    "K": [aspect_j_rule26,],
    "L": [aspect_j_rule26,],
    "M": [aspect_j_rule26,],
    "N": [aspect_j_rule26,],
    "O": [aspect_j_rule26,],
    "P": [aspect_j_rule26,],
    "Q": [aspect_j_rule26,],
    "R": [aspect_j_rule26,],
    "S": [aspect_j_rule26,],
    "T": [aspect_j_rule26,],
    "U": [aspect_j_rule26,],
    "V": [aspect_j_rule26,],
    "W": [aspect_j_rule26,],
    "X": [aspect_j_rule26,],
    "Y": [aspect_j_rule26,],
    "Z": [aspect_j_rule26,],
    "^": [aspect_j_rule20,],
    "a": [aspect_j_rule26,],
    "b": [aspect_j_rule26,],
    "c": [aspect_j_rule26,],
    "d": [aspect_j_rule26,],
    "e": [aspect_j_rule26,],
    "f": [aspect_j_rule26,],
    "g": [aspect_j_rule26,],
    "h": [aspect_j_rule26,],
    "i": [aspect_j_rule26,],
    "j": [aspect_j_rule26,],
    "k": [aspect_j_rule26,],
    "l": [aspect_j_rule26,],
    "m": [aspect_j_rule26,],
    "n": [aspect_j_rule26,],
    "o": [aspect_j_rule26,],
    "p": [aspect_j_rule26,],
    "q": [aspect_j_rule26,],
    "r": [aspect_j_rule26,],
    "s": [aspect_j_rule26,],
    "t": [aspect_j_rule26,],
    "u": [aspect_j_rule26,],
    "v": [aspect_j_rule26,],
    "w": [aspect_j_rule26,],
    "x": [aspect_j_rule26,],
    "y": [aspect_j_rule26,],
    "z": [aspect_j_rule26,],
    "{": [aspect_j_rule23,],
    "|": [aspect_j_rule19,],
    "}": [aspect_j_rule22,],
    "~": [aspect_j_rule21,],
}

# x.rulesDictDict for aspect_j mode.
rulesDictDict = {
    "aspect_j_main": rulesDict1,
}

# Import dict for aspect_j mode.
importDict = {}
