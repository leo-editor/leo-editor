# Leo colorizer control file for prolog mode.
# This file is in the public domain.

# Properties for prolog mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "lineComment": "%",
}

# Attributes dict for prolog_main ruleset.
prolog_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for prolog_list ruleset.
prolog_list_attributes_dict = {
    "default": "LITERAL2",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for prolog mode.
attributesDictDict = {
    "prolog_list": prolog_list_attributes_dict,
    "prolog_main": prolog_main_attributes_dict,
}

# Keywords dict for prolog_main ruleset.
prolog_main_keywords_dict = {
    "!": "keyword1",
    "_": "keyword3",
    "abolish": "function",
    "arg": "function",
    "asserta": "function",
    "assertz": "function",
    "at_end_of_stream": "function",
    "atan": "function",
    "atom": "function",
    "atom_chars": "function",
    "atom_codes": "function",
    "atom_concat": "function",
    "atom_length": "function",
    "atomic": "function",
    "bagof": "function",
    "call": "function",
    "catch": "function",
    "char_code": "function",
    "char_conversion": "function",
    "clause": "function",
    "close": "function",
    "compound": "function",
    "copy_term": "function",
    "cos": "function",
    "current_char_conversion": "function",
    "current_input": "function",
    "current_op": "function",
    "current_output": "function",
    "current_predicate": "function",
    "current_prolog_flag": "function",
    "exp": "function",
    "fail": "keyword1",
    "findall": "function",
    "float": "function",
    "functor": "function",
    "get_byte": "function",
    "get_char": "function",
    "get_code": "function",
    "halt": "function",
    "integer": "function",
    "is": "keyword2",
    "log": "function",
    "mod": "keyword2",
    "nl": "function",
    "nonvar": "function",
    "number": "function",
    "number_chars": "function",
    "number_codes": "function",
    "once": "function",
    "op": "function",
    "open": "function",
    "peek_byte": "function",
    "peek_char": "function",
    "peek_code": "function",
    "put_byte": "function",
    "put_char": "function",
    "put_code": "function",
    "read": "function",
    "read_term": "function",
    "rem": "keyword2",
    "repeat": "keyword1",
    "retract": "function",
    "set_input": "function",
    "set_output": "function",
    "set_prolog_flag": "function",
    "set_stream_position": "function",
    "setof": "function",
    "sin": "function",
    "sqrt": "function",
    "stream_property": "function",
    "sub_atom": "function",
    "throw": "function",
    "true": "keyword1",
    "unify_with_occurs_check": "function",
    "var": "function",
    "write": "function",
    "write_canonical": "function",
    "write_term": "function",
    "writeq": "function",
}

# Keywords dict for prolog_list ruleset.
prolog_list_keywords_dict = {}

# Dictionary of keywords dictionaries for prolog mode.
keywordsDictDict = {
    "prolog_list": prolog_list_keywords_dict,
    "prolog_main": prolog_main_keywords_dict,
}

# Rules for prolog_main ruleset.

def prolog_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="%")

def prolog_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def prolog_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def prolog_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def prolog_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="[", end="]",
          delegate="prolog::list",
          no_line_break=True)

def prolog_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-->")

def prolog_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":-")

def prolog_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?-")

def prolog_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def prolog_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="->")

def prolog_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def prolog_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\+")

def prolog_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def prolog_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\==")

def prolog_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\=")

def prolog_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@<")

def prolog_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@=<")

def prolog_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@>=")

def prolog_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@>")

def prolog_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=..")

def prolog_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=:=")

def prolog_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=\\=")

def prolog_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=<")

def prolog_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def prolog_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def prolog_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def prolog_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/\\")

def prolog_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\/")

def prolog_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="//")

def prolog_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<<")

def prolog_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def prolog_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>")

def prolog_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def prolog_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="**")

def prolog_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def prolog_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def prolog_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def prolog_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def prolog_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def prolog_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def prolog_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="(")

def prolog_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq=")")

def prolog_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="{")

def prolog_rule43(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="}")

def prolog_rule44(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for prolog_main ruleset.
rulesDict1 = {
    "!": [prolog_rule44,],
    "\"": [prolog_rule3,],
    "%": [prolog_rule0,],
    "'": [prolog_rule2,],
    "(": [prolog_rule40,],
    ")": [prolog_rule41,],
    "*": [prolog_rule33, prolog_rule38,],
    "+": [prolog_rule24,],
    ",": [prolog_rule10,],
    "-": [prolog_rule5, prolog_rule9, prolog_rule25,],
    ".": [prolog_rule39,],
    "/": [prolog_rule1, prolog_rule26, prolog_rule28, prolog_rule36,],
    "0": [prolog_rule44,],
    "1": [prolog_rule44,],
    "2": [prolog_rule44,],
    "3": [prolog_rule44,],
    "4": [prolog_rule44,],
    "5": [prolog_rule44,],
    "6": [prolog_rule44,],
    "7": [prolog_rule44,],
    "8": [prolog_rule44,],
    "9": [prolog_rule44,],
    ":": [prolog_rule6,],
    ";": [prolog_rule8,],
    "<": [prolog_rule29, prolog_rule30,],
    "=": [prolog_rule12, prolog_rule19, prolog_rule20, prolog_rule21, prolog_rule22, prolog_rule37,],
    ">": [prolog_rule23, prolog_rule31, prolog_rule32,],
    "?": [prolog_rule7,],
    "@": [prolog_rule15, prolog_rule16, prolog_rule17, prolog_rule18, prolog_rule44,],
    "A": [prolog_rule44,],
    "B": [prolog_rule44,],
    "C": [prolog_rule44,],
    "D": [prolog_rule44,],
    "E": [prolog_rule44,],
    "F": [prolog_rule44,],
    "G": [prolog_rule44,],
    "H": [prolog_rule44,],
    "I": [prolog_rule44,],
    "J": [prolog_rule44,],
    "K": [prolog_rule44,],
    "L": [prolog_rule44,],
    "M": [prolog_rule44,],
    "N": [prolog_rule44,],
    "O": [prolog_rule44,],
    "P": [prolog_rule44,],
    "Q": [prolog_rule44,],
    "R": [prolog_rule44,],
    "S": [prolog_rule44,],
    "T": [prolog_rule44,],
    "U": [prolog_rule44,],
    "V": [prolog_rule44,],
    "W": [prolog_rule44,],
    "X": [prolog_rule44,],
    "Y": [prolog_rule44,],
    "Z": [prolog_rule44,],
    "[": [prolog_rule4,],
    "\\": [prolog_rule11, prolog_rule13, prolog_rule14, prolog_rule27, prolog_rule35,],
    "^": [prolog_rule34,],
    "_": [prolog_rule44,],
    "a": [prolog_rule44,],
    "b": [prolog_rule44,],
    "c": [prolog_rule44,],
    "d": [prolog_rule44,],
    "e": [prolog_rule44,],
    "f": [prolog_rule44,],
    "g": [prolog_rule44,],
    "h": [prolog_rule44,],
    "i": [prolog_rule44,],
    "j": [prolog_rule44,],
    "k": [prolog_rule44,],
    "l": [prolog_rule44,],
    "m": [prolog_rule44,],
    "n": [prolog_rule44,],
    "o": [prolog_rule44,],
    "p": [prolog_rule44,],
    "q": [prolog_rule44,],
    "r": [prolog_rule44,],
    "s": [prolog_rule44,],
    "t": [prolog_rule44,],
    "u": [prolog_rule44,],
    "v": [prolog_rule44,],
    "w": [prolog_rule44,],
    "x": [prolog_rule44,],
    "y": [prolog_rule44,],
    "z": [prolog_rule44,],
    "{": [prolog_rule42,],
    "}": [prolog_rule43,],
}

# Rules for prolog_list ruleset.

def prolog_rule45(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="[", end="]",
          delegate="prolog::list",
          no_line_break=True)

# Rules dict for prolog_list ruleset.
rulesDict2 = {
    "[": [prolog_rule45,],
}

# x.rulesDictDict for prolog mode.
rulesDictDict = {
    "prolog_list": rulesDict2,
    "prolog_main": rulesDict1,
}

# Import dict for prolog mode.
importDict = {}
