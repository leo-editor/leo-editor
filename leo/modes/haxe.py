# Leo colorizer control file for haXe mode.
# This file is in the public domain.

# Properties for haXe mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "doubleBracketIndent": "false",
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "indentPrevLine": "\\s*(if|while)\\s*(|else|case|default:)[^;]*|for\\s*\\(.*)",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
    "wordBreakChars": "+-.,=<>/?^&*",
}

# Attributes dict for haxe_main ruleset.
haxe_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+|[[:digit:]]+((E|e|)[[:digit:]]*)?)",
    "escape": "\\\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for haxe mode.
attributesDictDict = {
    "haxe_main": haxe_main_attributes_dict,
}

# Keywords dict for haxe_main ruleset.
haxe_main_keywords_dict = {
    "Array": "keyword3",
    "ArrayAccess": "keyword3",
    "Bool": "keyword3",
    "Dynamic": "keyword3",
    "Float": "keyword3",
    "Int": "keyword3",
    "Iterable": "keyword3",
    "Iterator": "keyword3",
    "Null": "keyword3",
    "Object": "keyword3",
    "String": "keyword3",
    "UInt": "keyword3",
    "Void": "keyword3",
    "break": "keyword1",
    "case": "keyword1",
    "cast": "literal2",
    "catch": "keyword1",
    "class": "keyword2",
    "continue": "keyword1",
    "default": "keyword1",
    "do": "keyword1",
    "else": "keyword1",
    "enum": "keyword2",
    "extends": "keyword2",
    "extern": "keyword2",
    "false": "literal2",
    "for": "keyword1",
    "function": "keyword2",
    "if": "keyword1",
    "implements": "keyword2",
    "import": "keyword2",
    "in": "keyword1",
    "inline": "keyword2",
    "interface": "keyword2",
    "new": "literal2",
    "null": "literal2",
    "override": "keyword2",
    "package": "keyword2",
    "private": "keyword2",
    "public": "keyword2",
    "return": "keyword1",
    "static": "keyword2",
    "super": "literal2",
    "switch": "keyword1",
    "this": "literal2",
    "throw": "keyword1",
    "trace": "literal2",
    "true": "literal2",
    "try": "keyword1",
    "typedef": "keyword2",
    "typeof": "literal2",
    "undefined": "literal2",
    "untyped": "literal2",
    "var": "keyword2",
    "while": "keyword1",
}

# Dictionary of keywords dictionaries for haxe mode.
keywordsDictDict = {
    "haxe_main": haxe_main_keywords_dict,
}

# Rules for haxe_main ruleset.

def haXe_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def haXe_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def haXe_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def haXe_rule3(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def haXe_rule4(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def haXe_rule5(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="//")

def haXe_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment3", seq="#")

def haXe_rule7(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="~([[:punct:]])(?:.*?[^\\\\])*?\\1[sgiexom]*")

def haXe_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=")")

def haXe_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="(")

def haXe_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def haXe_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def haXe_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def haXe_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def haXe_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def haXe_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def haXe_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def haXe_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def haXe_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def haXe_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def haXe_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def haXe_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def haXe_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def haXe_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def haXe_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def haXe_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def haXe_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def haXe_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def haXe_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def haXe_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def haXe_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def haXe_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def haXe_rule32(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for haxe_main ruleset.
rulesDict1 = {
    "!": [haXe_rule11,],
    "\"": [haXe_rule1,],
    "#": [haXe_rule6,],
    "%": [haXe_rule18,],
    "&": [haXe_rule19,],
    "'": [haXe_rule2,],
    "(": [haXe_rule3, haXe_rule4, haXe_rule9,],
    ")": [haXe_rule8,],
    "*": [haXe_rule15,],
    "+": [haXe_rule12,],
    ",": [haXe_rule26,],
    "-": [haXe_rule13,],
    ".": [haXe_rule23,],
    "/": [haXe_rule0, haXe_rule5, haXe_rule14,],
    "0": [haXe_rule32,],
    "1": [haXe_rule32,],
    "2": [haXe_rule32,],
    "3": [haXe_rule32,],
    "4": [haXe_rule32,],
    "5": [haXe_rule32,],
    "6": [haXe_rule32,],
    "7": [haXe_rule32,],
    "8": [haXe_rule32,],
    "9": [haXe_rule32,],
    ":": [haXe_rule31,],
    ";": [haXe_rule27,],
    "<": [haXe_rule17,],
    "=": [haXe_rule10,],
    ">": [haXe_rule16,],
    "?": [haXe_rule30,],
    "@": [haXe_rule32,],
    "A": [haXe_rule32,],
    "B": [haXe_rule32,],
    "C": [haXe_rule32,],
    "D": [haXe_rule32,],
    "E": [haXe_rule32,],
    "F": [haXe_rule32,],
    "G": [haXe_rule32,],
    "H": [haXe_rule32,],
    "I": [haXe_rule32,],
    "J": [haXe_rule32,],
    "K": [haXe_rule32,],
    "L": [haXe_rule32,],
    "M": [haXe_rule32,],
    "N": [haXe_rule32,],
    "O": [haXe_rule32,],
    "P": [haXe_rule32,],
    "Q": [haXe_rule32,],
    "R": [haXe_rule32,],
    "S": [haXe_rule32,],
    "T": [haXe_rule32,],
    "U": [haXe_rule32,],
    "V": [haXe_rule32,],
    "W": [haXe_rule32,],
    "X": [haXe_rule32,],
    "Y": [haXe_rule32,],
    "Z": [haXe_rule32,],
    "[": [haXe_rule29,],
    "]": [haXe_rule28,],
    "^": [haXe_rule21,],
    "a": [haXe_rule32,],
    "b": [haXe_rule32,],
    "c": [haXe_rule32,],
    "d": [haXe_rule32,],
    "e": [haXe_rule32,],
    "f": [haXe_rule32,],
    "g": [haXe_rule32,],
    "h": [haXe_rule32,],
    "i": [haXe_rule32,],
    "j": [haXe_rule32,],
    "k": [haXe_rule32,],
    "l": [haXe_rule32,],
    "m": [haXe_rule32,],
    "n": [haXe_rule32,],
    "o": [haXe_rule32,],
    "p": [haXe_rule32,],
    "q": [haXe_rule32,],
    "r": [haXe_rule32,],
    "s": [haXe_rule32,],
    "t": [haXe_rule32,],
    "u": [haXe_rule32,],
    "v": [haXe_rule32,],
    "w": [haXe_rule32,],
    "x": [haXe_rule32,],
    "y": [haXe_rule32,],
    "z": [haXe_rule32,],
    "{": [haXe_rule25,],
    "|": [haXe_rule20,],
    "}": [haXe_rule24,],
    "~": [haXe_rule7, haXe_rule22,],
}

# x.rulesDictDict for haxe mode.
rulesDictDict = {
    "haxe_main": rulesDict1,
}

# Import dict for haxe mode.
importDict = {}
