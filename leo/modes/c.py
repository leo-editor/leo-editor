# Leo colorizer control file for c mode.
# This file is in the public domain.

# Properties for c mode.
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

# Attributes dict for c_main ruleset.
c_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for c_cpp ruleset.
c_cpp_attributes_dict = {
    "default": "KEYWORD2",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for c_include ruleset.
c_include_attributes_dict = {
    "default": "KEYWORD2",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for c mode.
attributesDictDict = {
    "c_cpp": c_cpp_attributes_dict,
    "c_include": c_include_attributes_dict,
    "c_main": c_main_attributes_dict,
}

# Keywords dict for c_main ruleset.
c_main_keywords_dict = {
    "NULL": "literal2",
    "asm": "keyword2",
    "asmlinkage": "keyword2",
    "auto": "keyword1",
    "break": "keyword1",
    "case": "keyword1",
    "char": "keyword3",
    "const": "keyword1",
    "continue": "keyword1",
    "default": "keyword1",
    "do": "keyword1",
    "double": "keyword3",
    "else": "keyword1",
    "enum": "keyword3",
    "extern": "keyword1",
    "false": "literal2",
    "far": "keyword2",
    "float": "keyword3",
    "for": "keyword1",
    "goto": "keyword1",
    "huge": "keyword2",
    "if": "keyword1",
    "inline": "keyword2",
    "int": "keyword3",
    "long": "keyword3",
    "near": "keyword2",
    "pascal": "keyword2",
    "register": "keyword1",
    "return": "keyword1",
    "short": "keyword3",
    "signed": "keyword3",
    "sizeof": "keyword1",
    "static": "keyword1",
    "struct": "keyword3",
    "switch": "keyword1",
    "true": "literal2",
    "typedef": "keyword3",
    "union": "keyword3",
    "unsigned": "keyword3",
    "void": "keyword3",
    "volatile": "keyword1",
    "while": "keyword1",
}

# Keywords dict for c_cpp ruleset.
c_cpp_keywords_dict = {
    "assert": "markup",
    "define": "markup",
    "elif": "markup",
    "else": "markup",
    "endif": "markup",
    "error": "markup",
    "ident": "markup",
    "if": "markup",
    "ifdef": "markup",
    "ifndef": "markup",
    "import": "markup",
    "include": "markup",
    "include_next": "markup",
    "line": "markup",
    "pragma": "markup",
    "sccs": "markup",
    "unassert": "markup",
    "undef": "markup",
    "warning": "markup",
}

# Keywords dict for c_include ruleset.
c_include_keywords_dict = {}

# Dictionary of keywords dictionaries for c mode.
keywordsDictDict = {
    "c_cpp": c_cpp_keywords_dict,
    "c_include": c_include_keywords_dict,
    "c_main": c_main_keywords_dict,
}

# Rules for c_main ruleset.

def c_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="doxygen::doxygen")

def c_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/*!", end="*/",
          delegate="doxygen::doxygen")

def c_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def c_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def c_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def c_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="##")

def c_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#",
          delegate="c::cpp")

def c_rule7(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def c_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def c_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def c_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def c_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def c_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def c_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def c_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def c_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def c_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def c_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def c_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def c_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def c_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def c_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def c_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def c_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def c_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def c_rule25(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def c_rule26(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def c_rule27(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for c_main ruleset.
rulesDict1 = {
    "!": [c_rule9,],
    "\"": [c_rule3,],
    "#": [c_rule5, c_rule6,],
    "%": [c_rule18,],
    "&": [c_rule19,],
    "'": [c_rule4,],
    "(": [c_rule26,],
    "*": [c_rule15,],
    "+": [c_rule12,],
    "-": [c_rule13,],
    "/": [c_rule0, c_rule1, c_rule2, c_rule7, c_rule14,],
    "0": [c_rule27,],
    "1": [c_rule27,],
    "2": [c_rule27,],
    "3": [c_rule27,],
    "4": [c_rule27,],
    "5": [c_rule27,],
    "6": [c_rule27,],
    "7": [c_rule27,],
    "8": [c_rule27,],
    "9": [c_rule27,],
    ":": [c_rule25,],
    "<": [c_rule11, c_rule17,],
    "=": [c_rule8,],
    ">": [c_rule10, c_rule16,],
    "@": [c_rule27,],
    "A": [c_rule27,],
    "B": [c_rule27,],
    "C": [c_rule27,],
    "D": [c_rule27,],
    "E": [c_rule27,],
    "F": [c_rule27,],
    "G": [c_rule27,],
    "H": [c_rule27,],
    "I": [c_rule27,],
    "J": [c_rule27,],
    "K": [c_rule27,],
    "L": [c_rule27,],
    "M": [c_rule27,],
    "N": [c_rule27,],
    "O": [c_rule27,],
    "P": [c_rule27,],
    "Q": [c_rule27,],
    "R": [c_rule27,],
    "S": [c_rule27,],
    "T": [c_rule27,],
    "U": [c_rule27,],
    "V": [c_rule27,],
    "W": [c_rule27,],
    "X": [c_rule27,],
    "Y": [c_rule27,],
    "Z": [c_rule27,],
    "^": [c_rule21,],
    "_": [c_rule27,],
    "a": [c_rule27,],
    "b": [c_rule27,],
    "c": [c_rule27,],
    "d": [c_rule27,],
    "e": [c_rule27,],
    "f": [c_rule27,],
    "g": [c_rule27,],
    "h": [c_rule27,],
    "i": [c_rule27,],
    "j": [c_rule27,],
    "k": [c_rule27,],
    "l": [c_rule27,],
    "m": [c_rule27,],
    "n": [c_rule27,],
    "o": [c_rule27,],
    "p": [c_rule27,],
    "q": [c_rule27,],
    "r": [c_rule27,],
    "s": [c_rule27,],
    "t": [c_rule27,],
    "u": [c_rule27,],
    "v": [c_rule27,],
    "w": [c_rule27,],
    "x": [c_rule27,],
    "y": [c_rule27,],
    "z": [c_rule27,],
    "{": [c_rule24,],
    "|": [c_rule20,],
    "}": [c_rule23,],
    "~": [c_rule22,],
}

# Rules for c_cpp ruleset.

def c_rule28(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def c_rule29(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="markup", seq="include",
          delegate="c::include")

def c_rule30(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for c_cpp ruleset.
rulesDict2 = {
    "/": [c_rule28,],
    "0": [c_rule30,],
    "1": [c_rule30,],
    "2": [c_rule30,],
    "3": [c_rule30,],
    "4": [c_rule30,],
    "5": [c_rule30,],
    "6": [c_rule30,],
    "7": [c_rule30,],
    "8": [c_rule30,],
    "9": [c_rule30,],
    "@": [c_rule30,],
    "A": [c_rule30,],
    "B": [c_rule30,],
    "C": [c_rule30,],
    "D": [c_rule30,],
    "E": [c_rule30,],
    "F": [c_rule30,],
    "G": [c_rule30,],
    "H": [c_rule30,],
    "I": [c_rule30,],
    "J": [c_rule30,],
    "K": [c_rule30,],
    "L": [c_rule30,],
    "M": [c_rule30,],
    "N": [c_rule30,],
    "O": [c_rule30,],
    "P": [c_rule30,],
    "Q": [c_rule30,],
    "R": [c_rule30,],
    "S": [c_rule30,],
    "T": [c_rule30,],
    "U": [c_rule30,],
    "V": [c_rule30,],
    "W": [c_rule30,],
    "X": [c_rule30,],
    "Y": [c_rule30,],
    "Z": [c_rule30,],
    "_": [c_rule30,],
    "a": [c_rule30,],
    "b": [c_rule30,],
    "c": [c_rule30,],
    "d": [c_rule30,],
    "e": [c_rule30,],
    "f": [c_rule30,],
    "g": [c_rule30,],
    "h": [c_rule30,],
    "i": [c_rule29, c_rule30,],
    "j": [c_rule30,],
    "k": [c_rule30,],
    "l": [c_rule30,],
    "m": [c_rule30,],
    "n": [c_rule30,],
    "o": [c_rule30,],
    "p": [c_rule30,],
    "q": [c_rule30,],
    "r": [c_rule30,],
    "s": [c_rule30,],
    "t": [c_rule30,],
    "u": [c_rule30,],
    "v": [c_rule30,],
    "w": [c_rule30,],
    "x": [c_rule30,],
    "y": [c_rule30,],
    "z": [c_rule30,],
}

# Rules for c_include ruleset.

# Rules dict for c_include ruleset.
rulesDict3 = {}

# x.rulesDictDict for c mode.
rulesDictDict = {
    "c_cpp": rulesDict2,
    "c_include": rulesDict3,
    "c_main": rulesDict1,
}

# Import dict for c mode.
importDict = {}
