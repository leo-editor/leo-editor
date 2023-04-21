# Leo colorizer control file for csharp mode.
# This file is in the public domain.

# Properties for csharp mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "doubleBracketIndent": "false",
    "indentCloseBrackets": "}",
    "indentNextLine": "\\s*(((if|while)\\s*\\(|else\\s*|else\\s+if\\s*\\(|for\\s*\\(.*\\))[^{;]*)",
    "indentOpenBrackets": "{",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
}

# Attributes dict for csharp_main ruleset.
csharp_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for csharp_doc_comment ruleset.
csharp_doc_comment_attributes_dict = {
    "default": "COMMENT3",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for csharp mode.
attributesDictDict = {
    "csharp_doc_comment": csharp_doc_comment_attributes_dict,
    "csharp_main": csharp_main_attributes_dict,
}

# Keywords dict for csharp_main ruleset.
csharp_main_keywords_dict = {
    "abstract": "keyword1",
    "as": "keyword1",
    "base": "keyword1",
    "bool": "keyword3",
    "break": "keyword1",
    "byte": "keyword3",
    "case": "keyword1",
    "catch": "keyword1",
    "char": "keyword3",
    "checked": "keyword1",
    "class": "keyword3",
    "const": "keyword1",
    "continue": "keyword1",
    "decimal": "keyword1",
    "default": "keyword1",
    "delegate": "keyword1",
    "do": "keyword1",
    "double": "keyword3",
    "else": "keyword1",
    "enum": "keyword3",
    "event": "keyword3",
    "explicit": "keyword1",
    "extern": "keyword1",
    "false": "literal2",
    "finally": "keyword1",
    "fixed": "keyword1",
    "float": "keyword3",
    "for": "keyword1",
    "foreach": "keyword1",
    "goto": "keyword1",
    "if": "keyword1",
    "implicit": "keyword1",
    "in": "keyword1",
    "int": "keyword3",
    "interface": "keyword3",
    "internal": "keyword1",
    "is": "keyword1",
    "lock": "keyword1",
    "long": "keyword3",
    "namespace": "keyword2",
    "new": "keyword1",
    "null": "literal2",
    "object": "keyword3",
    "operator": "keyword1",
    "out": "keyword1",
    "override": "keyword1",
    "params": "keyword1",
    "private": "keyword1",
    "protected": "keyword1",
    "public": "keyword1",
    "readonly": "keyword1",
    "ref": "keyword1",
    "return": "keyword1",
    "sbyte": "keyword3",
    "sealed": "keyword1",
    "short": "keyword3",
    "sizeof": "keyword1",
    "stackalloc": "keyword1",
    "static": "keyword1",
    "string": "keyword3",
    "struct": "keyword3",
    "switch": "keyword1",
    "this": "literal2",
    "throw": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "typeof": "keyword1",
    "uint": "keyword3",
    "ulong": "keyword3",
    "unchecked": "keyword1",
    "unsafe": "keyword1",
    "ushort": "keyword3",
    "using": "keyword2",
    "virtual": "keyword1",
    "void": "keyword3",
    "while": "keyword1",
}

# Keywords dict for csharp_doc_comment ruleset.
csharp_doc_comment_keywords_dict = {}

# Dictionary of keywords dictionaries for csharp mode.
keywordsDictDict = {
    "csharp_doc_comment": csharp_doc_comment_keywords_dict,
    "csharp_main": csharp_main_keywords_dict,
}

# Rules for csharp_main ruleset.

def csharp_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def csharp_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment3", seq="///",
          delegate="csharp::doc_comment")

def csharp_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def csharp_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="@\"", end="\"",
          no_escape=True)

def csharp_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def csharp_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def csharp_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#if")

def csharp_rule7(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#else")

def csharp_rule8(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#elif")

def csharp_rule9(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#endif")

def csharp_rule10(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#define")

def csharp_rule11(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#undef")

def csharp_rule12(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#warning")

def csharp_rule13(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#error")

def csharp_rule14(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#line")

def csharp_rule15(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#region")

def csharp_rule16(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#endregion")

def csharp_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def csharp_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def csharp_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def csharp_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def csharp_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def csharp_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def csharp_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def csharp_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def csharp_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def csharp_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def csharp_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def csharp_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def csharp_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def csharp_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def csharp_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def csharp_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def csharp_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def csharp_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def csharp_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def csharp_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def csharp_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def csharp_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def csharp_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def csharp_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def csharp_rule41(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def csharp_rule42(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for csharp_main ruleset.
rulesDict1 = {
    "!": [csharp_rule18, csharp_rule25,],
    "\"": [csharp_rule4,],
    "#": [csharp_rule6, csharp_rule7, csharp_rule8, csharp_rule9, csharp_rule10, csharp_rule11, csharp_rule12, csharp_rule13, csharp_rule14, csharp_rule15, csharp_rule16,],
    "%": [csharp_rule39,],
    "&": [csharp_rule38,],
    "'": [csharp_rule5,],
    "(": [csharp_rule41,],
    "*": [csharp_rule33,],
    "+": [csharp_rule28,],
    ",": [csharp_rule23,],
    "-": [csharp_rule29,],
    ".": [csharp_rule24,],
    "/": [csharp_rule0, csharp_rule1, csharp_rule2, csharp_rule34,],
    "0": [csharp_rule42,],
    "1": [csharp_rule42,],
    "2": [csharp_rule42,],
    "3": [csharp_rule42,],
    "4": [csharp_rule42,],
    "5": [csharp_rule42,],
    "6": [csharp_rule42,],
    "7": [csharp_rule42,],
    "8": [csharp_rule42,],
    "9": [csharp_rule42,],
    ":": [csharp_rule19,],
    ";": [csharp_rule20,],
    "<": [csharp_rule31,],
    "=": [csharp_rule32,],
    ">": [csharp_rule30,],
    "?": [csharp_rule40,],
    "@": [csharp_rule3, csharp_rule42,],
    "A": [csharp_rule42,],
    "B": [csharp_rule42,],
    "C": [csharp_rule42,],
    "D": [csharp_rule42,],
    "E": [csharp_rule42,],
    "F": [csharp_rule42,],
    "G": [csharp_rule42,],
    "H": [csharp_rule42,],
    "I": [csharp_rule42,],
    "J": [csharp_rule42,],
    "K": [csharp_rule42,],
    "L": [csharp_rule42,],
    "M": [csharp_rule42,],
    "N": [csharp_rule42,],
    "O": [csharp_rule42,],
    "P": [csharp_rule42,],
    "Q": [csharp_rule42,],
    "R": [csharp_rule42,],
    "S": [csharp_rule42,],
    "T": [csharp_rule42,],
    "U": [csharp_rule42,],
    "V": [csharp_rule42,],
    "W": [csharp_rule42,],
    "X": [csharp_rule42,],
    "Y": [csharp_rule42,],
    "Z": [csharp_rule42,],
    "[": [csharp_rule26,],
    "\\": [csharp_rule35,],
    "]": [csharp_rule27,],
    "^": [csharp_rule36,],
    "a": [csharp_rule42,],
    "b": [csharp_rule42,],
    "c": [csharp_rule42,],
    "d": [csharp_rule42,],
    "e": [csharp_rule42,],
    "f": [csharp_rule42,],
    "g": [csharp_rule42,],
    "h": [csharp_rule42,],
    "i": [csharp_rule42,],
    "j": [csharp_rule42,],
    "k": [csharp_rule42,],
    "l": [csharp_rule42,],
    "m": [csharp_rule42,],
    "n": [csharp_rule42,],
    "o": [csharp_rule42,],
    "p": [csharp_rule42,],
    "q": [csharp_rule42,],
    "r": [csharp_rule42,],
    "s": [csharp_rule42,],
    "t": [csharp_rule42,],
    "u": [csharp_rule42,],
    "v": [csharp_rule42,],
    "w": [csharp_rule42,],
    "x": [csharp_rule42,],
    "y": [csharp_rule42,],
    "z": [csharp_rule42,],
    "{": [csharp_rule21,],
    "|": [csharp_rule37,],
    "}": [csharp_rule22,],
    "~": [csharp_rule17,],
}

# Rules for csharp_doc_comment ruleset.

def csharp_rule43(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<--", end="-->")

def csharp_rule44(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="xml::tags")

# Rules dict for csharp_doc_comment ruleset.
rulesDict2 = {
    "<": [csharp_rule43, csharp_rule44,],
}

# x.rulesDictDict for csharp mode.
rulesDictDict = {
    "csharp_doc_comment": rulesDict2,
    "csharp_main": rulesDict1,
}

# Import dict for csharp mode.
importDict = {}
