# Leo colorizer control file for java mode.
# This file is in the public domain.

# Properties for java mode.
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

# Attributes dict for java_main ruleset.
java_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for java_javadoc ruleset.
java_javadoc_attributes_dict = {
    "default": "COMMENT3",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for java mode.
attributesDictDict = {
    "java_javadoc": java_javadoc_attributes_dict,
    "java_main": java_main_attributes_dict,
}

# Keywords dict for java_main ruleset.
java_main_keywords_dict = {
    "abstract": "keyword1",
    "assert": "function",
    "boolean": "keyword3",
    "break": "keyword1",
    "byte": "keyword3",
    "case": "keyword1",
    "catch": "keyword1",
    "char": "keyword3",
    "class": "keyword3",
    "const": "invalid",
    "continue": "keyword1",
    "default": "keyword1",
    "do": "keyword1",
    "double": "keyword3",
    "else": "keyword1",
    "enum": "keyword3",
    "extends": "keyword1",
    "false": "literal2",
    "final": "keyword1",
    "finally": "keyword1",
    "float": "keyword3",
    "for": "keyword1",
    "goto": "invalid",
    "if": "keyword1",
    "implements": "keyword1",
    "import": "keyword2",
    "instanceof": "keyword1",
    "int": "keyword3",
    "interface": "keyword3",
    "long": "keyword3",
    "native": "keyword1",
    "new": "keyword1",
    "null": "literal2",
    "package": "keyword2",
    "private": "keyword1",
    "protected": "keyword1",
    "public": "keyword1",
    "return": "keyword1",
    "short": "keyword3",
    "static": "keyword1",
    "strictfp": "keyword1",
    "super": "literal2",
    "switch": "keyword1",
    "synchronized": "keyword1",
    "this": "literal2",
    "throw": "keyword1",
    "throws": "keyword1",
    "transient": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "void": "keyword3",
    "volatile": "keyword1",
    "while": "keyword1",
}

# Keywords dict for java_javadoc ruleset.
java_javadoc_keywords_dict = {
    "@access": "label",
    "@author": "label",
    "@beaninfo": "label",
    "@bon": "label",
    "@bug": "label",
    "@complexity": "label",
    "@deprecated": "label",
    "@design": "label",
    "@docroot": "label",
    "@ensures": "label",
    "@equivalent": "label",
    "@example": "label",
    "@exception": "label",
    "@generates": "label",
    "@guard": "label",
    "@hides": "label",
    "@history": "label",
    "@idea": "label",
    "@invariant": "label",
    "@link": "label",
    "@modifies": "label",
    "@overrides": "label",
    "@param": "label",
    "@post": "label",
    "@pre": "label",
    "@references": "label",
    "@requires": "label",
    "@return": "label",
    "@review": "label",
    "@see": "label",
    "@serial": "label",
    "@serialdata": "label",
    "@serialfield": "label",
    "@since": "label",
    "@spec": "label",
    "@throws": "label",
    "@todo": "label",
    "@uses": "label",
    "@values": "label",
    "@version": "label",
}

# Dictionary of keywords dictionaries for java mode.
keywordsDictDict = {
    "java_javadoc": java_javadoc_keywords_dict,
    "java_main": java_main_keywords_dict,
}

# Rules for java_main ruleset.

def java_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment1", seq="/**/")

def java_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="java::javadoc")

def java_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def java_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def java_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def java_rule5(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def java_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def java_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def java_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def java_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def java_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def java_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def java_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def java_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=".*")

def java_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def java_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def java_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def java_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def java_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def java_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def java_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def java_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def java_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def java_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def java_rule24(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def java_rule25(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def java_rule26(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword4", pattern="@")

def java_rule27(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for java_main ruleset.
rulesDict1 = {
    "!": [java_rule7,],
    "\"": [java_rule3,],
    "%": [java_rule17,],
    "&": [java_rule18,],
    "'": [java_rule4,],
    "(": [java_rule25,],
    "*": [java_rule14,],
    "+": [java_rule10,],
    "-": [java_rule11,],
    ".": [java_rule13,],
    "/": [java_rule0, java_rule1, java_rule2, java_rule5, java_rule12,],
    "0": [java_rule27,],
    "1": [java_rule27,],
    "2": [java_rule27,],
    "3": [java_rule27,],
    "4": [java_rule27,],
    "5": [java_rule27,],
    "6": [java_rule27,],
    "7": [java_rule27,],
    "8": [java_rule27,],
    "9": [java_rule27,],
    ":": [java_rule24,],
    "<": [java_rule9, java_rule16,],
    "=": [java_rule6,],
    ">": [java_rule8, java_rule15,],
    "@": [java_rule26, java_rule27,],
    "A": [java_rule27,],
    "B": [java_rule27,],
    "C": [java_rule27,],
    "D": [java_rule27,],
    "E": [java_rule27,],
    "F": [java_rule27,],
    "G": [java_rule27,],
    "H": [java_rule27,],
    "I": [java_rule27,],
    "J": [java_rule27,],
    "K": [java_rule27,],
    "L": [java_rule27,],
    "M": [java_rule27,],
    "N": [java_rule27,],
    "O": [java_rule27,],
    "P": [java_rule27,],
    "Q": [java_rule27,],
    "R": [java_rule27,],
    "S": [java_rule27,],
    "T": [java_rule27,],
    "U": [java_rule27,],
    "V": [java_rule27,],
    "W": [java_rule27,],
    "X": [java_rule27,],
    "Y": [java_rule27,],
    "Z": [java_rule27,],
    "^": [java_rule20,],
    "a": [java_rule27,],
    "b": [java_rule27,],
    "c": [java_rule27,],
    "d": [java_rule27,],
    "e": [java_rule27,],
    "f": [java_rule27,],
    "g": [java_rule27,],
    "h": [java_rule27,],
    "i": [java_rule27,],
    "j": [java_rule27,],
    "k": [java_rule27,],
    "l": [java_rule27,],
    "m": [java_rule27,],
    "n": [java_rule27,],
    "o": [java_rule27,],
    "p": [java_rule27,],
    "q": [java_rule27,],
    "r": [java_rule27,],
    "s": [java_rule27,],
    "t": [java_rule27,],
    "u": [java_rule27,],
    "v": [java_rule27,],
    "w": [java_rule27,],
    "x": [java_rule27,],
    "y": [java_rule27,],
    "z": [java_rule27,],
    "{": [java_rule23,],
    "|": [java_rule19,],
    "}": [java_rule22,],
    "~": [java_rule21,],
}

# Rules for java_javadoc ruleset.

def java_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="{")

def java_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="*")

def java_rule30(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def java_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="<<")

def java_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="<=")

def java_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="< ")

def java_rule34(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="xml::tags",
          no_line_break=True)

def java_rule35(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for java_javadoc ruleset.
rulesDict2 = {
    "*": [java_rule29,],
    "0": [java_rule35,],
    "1": [java_rule35,],
    "2": [java_rule35,],
    "3": [java_rule35,],
    "4": [java_rule35,],
    "5": [java_rule35,],
    "6": [java_rule35,],
    "7": [java_rule35,],
    "8": [java_rule35,],
    "9": [java_rule35,],
    "<": [java_rule30, java_rule31, java_rule32, java_rule33, java_rule34,],
    "@": [java_rule35,],
    "A": [java_rule35,],
    "B": [java_rule35,],
    "C": [java_rule35,],
    "D": [java_rule35,],
    "E": [java_rule35,],
    "F": [java_rule35,],
    "G": [java_rule35,],
    "H": [java_rule35,],
    "I": [java_rule35,],
    "J": [java_rule35,],
    "K": [java_rule35,],
    "L": [java_rule35,],
    "M": [java_rule35,],
    "N": [java_rule35,],
    "O": [java_rule35,],
    "P": [java_rule35,],
    "Q": [java_rule35,],
    "R": [java_rule35,],
    "S": [java_rule35,],
    "T": [java_rule35,],
    "U": [java_rule35,],
    "V": [java_rule35,],
    "W": [java_rule35,],
    "X": [java_rule35,],
    "Y": [java_rule35,],
    "Z": [java_rule35,],
    "a": [java_rule35,],
    "b": [java_rule35,],
    "c": [java_rule35,],
    "d": [java_rule35,],
    "e": [java_rule35,],
    "f": [java_rule35,],
    "g": [java_rule35,],
    "h": [java_rule35,],
    "i": [java_rule35,],
    "j": [java_rule35,],
    "k": [java_rule35,],
    "l": [java_rule35,],
    "m": [java_rule35,],
    "n": [java_rule35,],
    "o": [java_rule35,],
    "p": [java_rule35,],
    "q": [java_rule35,],
    "r": [java_rule35,],
    "s": [java_rule35,],
    "t": [java_rule35,],
    "u": [java_rule35,],
    "v": [java_rule35,],
    "w": [java_rule35,],
    "x": [java_rule35,],
    "y": [java_rule35,],
    "z": [java_rule35,],
    "{": [java_rule28,],
}

# x.rulesDictDict for java mode.
rulesDictDict = {
    "java_javadoc": rulesDict2,
    "java_main": rulesDict1,
}

# Import dict for java mode.
importDict = {}
