# Leo colorizer control file for antlr mode.
# This file is in the public domain.

# Properties for antlr mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "lineComment": "//",
    "wordBreakChars": "",
}

# Attributes dict for antlr_main ruleset.
antlr_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for antlr mode.
attributesDictDict = {
    "antlr_main": antlr_main_attributes_dict,
}

# Keywords dict for antlr_main ruleset.
antlr_main_keywords_dict = {
    "abstract": "keyword1",
    "assert": "function",
    "boolean": "keyword2",
    "break": "keyword1",
    "byte": "keyword2",
    "case": "keyword1",
    "catch": "keyword1",
    "char": "keyword2",
    "class": "keyword2",
    "const": "invalid",
    "continue": "keyword1",
    "default": "keyword1",
    "do": "keyword1",
    "double": "keyword2",
    "else": "keyword1",
    "extends": "keyword1",
    "false": "literal2",
    "final": "keyword1",
    "finally": "keyword1",
    "float": "keyword2",
    "for": "keyword1",
    "goto": "invalid",
    "header": "keyword3",
    "if": "keyword1",
    "implements": "keyword1",
    "import": "keyword1",
    "instanceof": "keyword1",
    "int": "keyword2",
    "interface": "keyword2",
    "long": "keyword2",
    "native": "keyword1",
    "new": "keyword1",
    "null": "literal2",
    "options": "keyword3",
    "package": "keyword1",
    "private": "keyword1",
    "protected": "keyword1",
    "public": "keyword1",
    "return": "keyword1",
    "short": "keyword2",
    "static": "keyword1",
    "strictfp": "keyword1",
    "super": "literal2",
    "switch": "keyword1",
    "synchronized": "keyword1",
    "this": "literal2",
    "throw": "keyword1",
    "throws": "keyword1",
    "tokens": "keyword3",
    "transient": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "void": "keyword2",
    "volatile": "keyword1",
    "while": "keyword1",
}

# Dictionary of keywords dictionaries for antlr mode.
keywordsDictDict = {
    "antlr_main": antlr_main_keywords_dict,
}

# Rules for antlr_main ruleset.

def antlr_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="/**", end="*/",
          delegate="java::javadoc")

def antlr_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def antlr_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="//")

def antlr_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def antlr_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def antlr_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def antlr_rule6(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for antlr_main ruleset.
rulesDict1 = {
    "\"": [antlr_rule3,],
    "/": [antlr_rule0, antlr_rule1, antlr_rule2,],
    "0": [antlr_rule6,],
    "1": [antlr_rule6,],
    "2": [antlr_rule6,],
    "3": [antlr_rule6,],
    "4": [antlr_rule6,],
    "5": [antlr_rule6,],
    "6": [antlr_rule6,],
    "7": [antlr_rule6,],
    "8": [antlr_rule6,],
    "9": [antlr_rule6,],
    ":": [antlr_rule5,],
    "@": [antlr_rule6,],
    "A": [antlr_rule6,],
    "B": [antlr_rule6,],
    "C": [antlr_rule6,],
    "D": [antlr_rule6,],
    "E": [antlr_rule6,],
    "F": [antlr_rule6,],
    "G": [antlr_rule6,],
    "H": [antlr_rule6,],
    "I": [antlr_rule6,],
    "J": [antlr_rule6,],
    "K": [antlr_rule6,],
    "L": [antlr_rule6,],
    "M": [antlr_rule6,],
    "N": [antlr_rule6,],
    "O": [antlr_rule6,],
    "P": [antlr_rule6,],
    "Q": [antlr_rule6,],
    "R": [antlr_rule6,],
    "S": [antlr_rule6,],
    "T": [antlr_rule6,],
    "U": [antlr_rule6,],
    "V": [antlr_rule6,],
    "W": [antlr_rule6,],
    "X": [antlr_rule6,],
    "Y": [antlr_rule6,],
    "Z": [antlr_rule6,],
    "a": [antlr_rule6,],
    "b": [antlr_rule6,],
    "c": [antlr_rule6,],
    "d": [antlr_rule6,],
    "e": [antlr_rule6,],
    "f": [antlr_rule6,],
    "g": [antlr_rule6,],
    "h": [antlr_rule6,],
    "i": [antlr_rule6,],
    "j": [antlr_rule6,],
    "k": [antlr_rule6,],
    "l": [antlr_rule6,],
    "m": [antlr_rule6,],
    "n": [antlr_rule6,],
    "o": [antlr_rule6,],
    "p": [antlr_rule6,],
    "q": [antlr_rule6,],
    "r": [antlr_rule6,],
    "s": [antlr_rule6,],
    "t": [antlr_rule6,],
    "u": [antlr_rule6,],
    "v": [antlr_rule6,],
    "w": [antlr_rule6,],
    "x": [antlr_rule6,],
    "y": [antlr_rule6,],
    "z": [antlr_rule6,],
    "|": [antlr_rule4,],
}

# x.rulesDictDict for antlr mode.
rulesDictDict = {
    "antlr_main": rulesDict1,
}

# Import dict for antlr mode.
importDict = {}
