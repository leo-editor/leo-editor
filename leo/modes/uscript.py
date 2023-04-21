# Leo colorizer control file for uscript mode.
# This file is in the public domain.

# Properties for uscript mode.
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

# Attributes dict for uscript_main ruleset.
uscript_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for uscript mode.
attributesDictDict = {
    "uscript_main": uscript_main_attributes_dict,
}

# Keywords dict for uscript_main ruleset.
uscript_main_keywords_dict = {
    "abstract": "keyword1",
    "array": "keyword1",
    "auto": "keyword1",
    "bool": "keyword3",
    "byte": "keyword3",
    "case": "keyword1",
    "class": "keyword1",
    "coerce": "keyword1",
    "collapscategories": "keyword1",
    "config": "keyword1",
    "const": "keyword1",
    "default": "keyword2",
    "defaultproperties": "keyword1",
    "deprecated": "keyword1",
    "do": "keyword1",
    "dontcollapsecategories": "keyword1",
    "edfindable": "keyword1",
    "editconst": "keyword1",
    "editinline": "keyword1",
    "editinlinenew": "keyword1",
    "else": "keyword1",
    "enum": "keyword1",
    "event": "keyword1",
    "exec": "keyword1",
    "export": "keyword1",
    "exportstructs": "keyword1",
    "extends": "keyword1",
    "false": "keyword1",
    "final": "keyword1",
    "float": "keyword3",
    "for": "keyword1",
    "foreach": "keyword1",
    "function": "keyword1",
    "global": "keyword2",
    "globalconfig": "keyword1",
    "hidecategories": "keyword1",
    "if": "keyword1",
    "ignores": "keyword1",
    "input": "keyword1",
    "int": "keyword3",
    "iterator": "keyword1",
    "latent": "keyword1",
    "local": "keyword1",
    "localized": "keyword1",
    "name": "keyword3",
    "native": "keyword1",
    "nativereplication": "keyword1",
    "noexport": "keyword1",
    "none": "keyword2",
    "noteditinlinenew": "keyword1",
    "notplaceable": "keyword1",
    "operator": "keyword1",
    "optional": "keyword1",
    "out": "keyword1",
    "perobjectconfig": "keyword1",
    "placeable": "keyword1",
    "postoperator": "keyword1",
    "preoperator": "keyword1",
    "private": "keyword1",
    "protected": "keyword1",
    "reliable": "keyword1",
    "replication": "keyword1",
    "return": "keyword1",
    "safereplace": "keyword1",
    "self": "keyword2",
    "showcategories": "keyword1",
    "simulated": "keyword1",
    "singular": "keyword1",
    "state": "keyword1",
    "static": "keyword2",
    "string": "keyword3",
    "struct": "keyword1",
    "super": "keyword2",
    "switch": "keyword1",
    "transient": "keyword1",
    "travel": "keyword1",
    "true": "keyword1",
    "unreliable": "keyword1",
    "until": "keyword1",
    "var": "keyword1",
    "while": "keyword1",
    "within": "keyword1",
}

# Dictionary of keywords dictionaries for uscript mode.
keywordsDictDict = {
    "uscript_main": uscript_main_keywords_dict,
}

# Rules for uscript_main ruleset.

def uscript_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment1", seq="/**/")

def uscript_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def uscript_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def uscript_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def uscript_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="//")

def uscript_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def uscript_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def uscript_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def uscript_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="#")

def uscript_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="$")

def uscript_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def uscript_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def uscript_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def uscript_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def uscript_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def uscript_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def uscript_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def uscript_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\\\")

def uscript_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def uscript_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def uscript_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def uscript_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def uscript_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def uscript_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="`")

def uscript_rule24(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def uscript_rule25(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def uscript_rule26(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for uscript_main ruleset.
rulesDict1 = {
    "!": [uscript_rule6,],
    "\"": [uscript_rule2,],
    "#": [uscript_rule8,],
    "$": [uscript_rule9,],
    "&": [uscript_rule11,],
    "'": [uscript_rule3,],
    "(": [uscript_rule25,],
    "*": [uscript_rule12,],
    "+": [uscript_rule15,],
    "-": [uscript_rule13,],
    "/": [uscript_rule0, uscript_rule1, uscript_rule4, uscript_rule21,],
    "0": [uscript_rule26,],
    "1": [uscript_rule26,],
    "2": [uscript_rule26,],
    "3": [uscript_rule26,],
    "4": [uscript_rule26,],
    "5": [uscript_rule26,],
    "6": [uscript_rule26,],
    "7": [uscript_rule26,],
    "8": [uscript_rule26,],
    "9": [uscript_rule26,],
    ":": [uscript_rule18, uscript_rule24,],
    "<": [uscript_rule19,],
    "=": [uscript_rule14,],
    ">": [uscript_rule20,],
    "?": [uscript_rule22,],
    "@": [uscript_rule7, uscript_rule26,],
    "A": [uscript_rule26,],
    "B": [uscript_rule26,],
    "C": [uscript_rule26,],
    "D": [uscript_rule26,],
    "E": [uscript_rule26,],
    "F": [uscript_rule26,],
    "G": [uscript_rule26,],
    "H": [uscript_rule26,],
    "I": [uscript_rule26,],
    "J": [uscript_rule26,],
    "K": [uscript_rule26,],
    "L": [uscript_rule26,],
    "M": [uscript_rule26,],
    "N": [uscript_rule26,],
    "O": [uscript_rule26,],
    "P": [uscript_rule26,],
    "Q": [uscript_rule26,],
    "R": [uscript_rule26,],
    "S": [uscript_rule26,],
    "T": [uscript_rule26,],
    "U": [uscript_rule26,],
    "V": [uscript_rule26,],
    "W": [uscript_rule26,],
    "X": [uscript_rule26,],
    "Y": [uscript_rule26,],
    "Z": [uscript_rule26,],
    "\\": [uscript_rule17,],
    "^": [uscript_rule10,],
    "`": [uscript_rule23,],
    "a": [uscript_rule26,],
    "b": [uscript_rule26,],
    "c": [uscript_rule26,],
    "d": [uscript_rule26,],
    "e": [uscript_rule26,],
    "f": [uscript_rule26,],
    "g": [uscript_rule26,],
    "h": [uscript_rule26,],
    "i": [uscript_rule26,],
    "j": [uscript_rule26,],
    "k": [uscript_rule26,],
    "l": [uscript_rule26,],
    "m": [uscript_rule26,],
    "n": [uscript_rule26,],
    "o": [uscript_rule26,],
    "p": [uscript_rule26,],
    "q": [uscript_rule26,],
    "r": [uscript_rule26,],
    "s": [uscript_rule26,],
    "t": [uscript_rule26,],
    "u": [uscript_rule26,],
    "v": [uscript_rule26,],
    "w": [uscript_rule26,],
    "x": [uscript_rule26,],
    "y": [uscript_rule26,],
    "z": [uscript_rule26,],
    "|": [uscript_rule16,],
    "~": [uscript_rule5,],
}

# x.rulesDictDict for uscript mode.
rulesDictDict = {
    "uscript_main": rulesDict1,
}

# Import dict for uscript mode.
importDict = {}
