#@+leo-ver=5-thin
#@+node:ekr.20250121105007.1: * @file ../modes/c.py
# Leo colorizer control file for c mode.
# This file is in the public domain.

#@+others
#@-others

#@+<< c: properties >>
#@+node:ekr.20250123062334.1: ** << c: properties >>

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
#@-<< c: properties >>
#@+<< c: attributes & dict >>
#@+node:ekr.20250123062356.1: ** << c: attributes & dict >>

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
#@-<< c: attributes & dict >>
#@+<< c: keywords dict >>
#@+node:ekr.20250123062431.1: ** << c: keywords dict >>

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
### c_include_keywords_dict = {}

# Dictionary of keywords dictionaries for c mode.
keywordsDictDict = {
    "c_cpp": c_cpp_keywords_dict,
    ### "c_include": c_include_keywords_dict,
    "c_main": c_main_keywords_dict,
}
#@-<< c: keywords dict >>
#@+<< c: rules >>
#@+node:ekr.20250123062533.1: ** << c: rules >>
# Rules for c_main ruleset.

#@+others
#@+node:ekr.20250123061808.1: *3* function: c_rule0
def c_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="doxygen::doxygen")
#@+node:ekr.20250123061808.2: *3* function: c_rule1
def c_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/*!", end="*/",
          delegate="doxygen::doxygen")
#@+node:ekr.20250123061808.3: *3* function: c_rule2 /* comment
def c_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")
#@+node:ekr.20250123061808.4: *3* function: c_rule3 "

def c_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)
#@+node:ekr.20250123061808.5: *3* function: c_rule4 '

def c_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)
#@+node:ekr.20250123061808.6: *3* function: c_rule5 ##
def c_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="##")
#@+node:ekr.20250123061808.7: *3* function: c_rule6 #
def c_rule6(colorer, s, i):

    # #4283: Colorizer the whole line.
    return colorer.match_eol_span(s, i, kind="keyword2")
#@+node:ekr.20250123061808.8: *3* function: c_rule7 // comment
def c_rule7(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")
#@+node:ekr.20250123070417.1: *3* rules: operators
#@+node:ekr.20250123061808.9: *4* function: c_rule8
def c_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")
#@+node:ekr.20250123061808.10: *4* function: c_rule9
def c_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")
#@+node:ekr.20250123061808.11: *4* function: c_rule10
def c_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")
#@+node:ekr.20250123061808.12: *4* function: c_rule11
def c_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")
#@+node:ekr.20250123061808.13: *4* function: c_rule12
def c_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")
#@+node:ekr.20250123061808.14: *4* function: c_rule13

def c_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")
#@+node:ekr.20250123061808.15: *4* function: c_rule14

def c_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")
#@+node:ekr.20250123061808.16: *4* function: c_rule15

def c_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")
#@+node:ekr.20250123061808.17: *4* function: c_rule16

def c_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")
#@+node:ekr.20250123061808.18: *4* function: c_rule17

def c_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")
#@+node:ekr.20250123061808.19: *4* function: c_rule18

def c_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")
#@+node:ekr.20250123061808.20: *4* function: c_rule19

def c_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")
#@+node:ekr.20250123061808.21: *4* function: c_rule20

def c_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")
#@+node:ekr.20250123061808.22: *4* function: c_rule21

def c_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")
#@+node:ekr.20250123061808.23: *4* function: c_rule22

def c_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")
#@+node:ekr.20250123061808.24: *4* function: c_rule23

def c_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")
#@+node:ekr.20250123061808.25: *4* function: c_rule24

def c_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")
#@+node:ekr.20250123061808.26: *3* function: c_rule25 : label

def c_rule25(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True, exclude_match=True)
#@+node:ekr.20250123061808.27: *3* function: c_rule26 (
def c_rule26(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)
#@+node:ekr.20250123061808.28: *3* function: c_rule27 keywords

def c_rule27(colorer, s, i):
    return colorer.match_keywords(s, i)
#@-others
#@-<< c: rules >>
#@+<< c: rules dict >>
#@+node:ekr.20250123062712.1: ** << c: rules dict >>
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
#@-<< c: rules dict >>

# x.rulesDictDict for c mode.
rulesDictDict = {
    "c_main": rulesDict1,
}

# Import dict for c mode.
importDict = {}

#@@language python
#@@tabwidth -4
#@-leo
