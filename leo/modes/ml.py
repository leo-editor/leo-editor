# Leo colorizer control file for ml mode.
# This file is in the public domain.

# Properties for ml mode.
properties = {
    "commentEnd": "*)",
    "commentStart": "(*",
}

# Attributes dict for ml_main ruleset.
ml_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for ml mode.
attributesDictDict = {
    "ml_main": ml_main_attributes_dict,
}

# Keywords dict for ml_main ruleset.
ml_main_keywords_dict = {
    "ANTIQUOTE": "literal2",
    "Bind": "keyword2",
    "Chr": "keyword2",
    "Div": "keyword2",
    "Domain": "keyword2",
    "EQUAL": "literal2",
    "Fail": "keyword2",
    "GREATER": "literal2",
    "Graphic": "keyword2",
    "Interrupt": "keyword2",
    "Io": "keyword2",
    "LESS": "literal2",
    "Match": "keyword2",
    "NONE": "literal2",
    "Option": "keyword2",
    "Ord": "keyword2",
    "Overflow": "keyword2",
    "QUOTE": "literal2",
    "SOME": "literal2",
    "Size": "keyword2",
    "Subscript": "keyword2",
    "SysErr": "keyword2",
    "abstype": "keyword1",
    "and": "keyword1",
    "andalso": "keyword1",
    "array": "keyword3",
    "as": "keyword1",
    "before": "operator",
    "bool": "keyword3",
    "case": "keyword1",
    "char": "keyword3",
    "datatype": "keyword1",
    "div": "operator",
    "do": "keyword1",
    "else": "keyword1",
    "end": "keyword1",
    "eqtype": "keyword1",
    "exception": "keyword1",
    "exn": "keyword3",
    "false": "literal2",
    "fn": "keyword1",
    "frag": "keyword3",
    "fun": "keyword1",
    "functor": "keyword1",
    "handle": "keyword1",
    "if": "keyword1",
    "in": "keyword1",
    "include": "keyword1",
    "infix": "keyword1",
    "infixr": "keyword1",
    "int": "keyword3",
    "let": "keyword1",
    "list": "keyword3",
    "local": "keyword1",
    "mod": "operator",
    "nil": "literal2",
    "nonfix": "keyword1",
    "o": "operator",
    "of": "keyword1",
    "op": "keyword1",
    "open": "keyword1",
    "option": "keyword3",
    "order": "keyword3",
    "orelse": "keyword1",
    "raise": "keyword1",
    "real": "keyword3",
    "rec": "keyword1",
    "ref": "keyword3",
    "sharing": "keyword1",
    "sig": "keyword1",
    "signature": "keyword1",
    "string": "keyword3",
    "struct": "keyword1",
    "structure": "keyword1",
    "substring": "keyword3",
    "then": "keyword1",
    "true": "literal2",
    "type": "keyword1",
    "unit": "keyword3",
    "val": "keyword1",
    "vector": "keyword3",
    "where": "keyword1",
    "while": "keyword1",
    "with": "keyword1",
    "withtype": "keyword1",
    "word": "keyword3",
    "word8": "keyword3",
}

# Dictionary of keywords dictionaries for ml mode.
keywordsDictDict = {
    "ml_main": ml_main_keywords_dict,
}

# Rules for ml_main ruleset.

def ml_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="(*", end="*)")

def ml_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="#\"", end="\"",
          no_line_break=True)

def ml_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def ml_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def ml_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def ml_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def ml_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def ml_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def ml_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="::")

def ml_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def ml_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def ml_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<>")

def ml_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def ml_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def ml_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def ml_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def ml_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def ml_rule17(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for ml_main ruleset.
rulesDict1 = {
    "\"": [ml_rule2,],
    "#": [ml_rule1,],
    "(": [ml_rule0,],
    "*": [ml_rule4,],
    "+": [ml_rule5,],
    "-": [ml_rule6,],
    "/": [ml_rule3,],
    "0": [ml_rule17,],
    "1": [ml_rule17,],
    "2": [ml_rule17,],
    "3": [ml_rule17,],
    "4": [ml_rule17,],
    "5": [ml_rule17,],
    "6": [ml_rule17,],
    "7": [ml_rule17,],
    "8": [ml_rule17,],
    "9": [ml_rule17,],
    ":": [ml_rule8, ml_rule16,],
    "<": [ml_rule11, ml_rule12, ml_rule13,],
    "=": [ml_rule10,],
    ">": [ml_rule14, ml_rule15,],
    "@": [ml_rule9, ml_rule17,],
    "A": [ml_rule17,],
    "B": [ml_rule17,],
    "C": [ml_rule17,],
    "D": [ml_rule17,],
    "E": [ml_rule17,],
    "F": [ml_rule17,],
    "G": [ml_rule17,],
    "H": [ml_rule17,],
    "I": [ml_rule17,],
    "J": [ml_rule17,],
    "K": [ml_rule17,],
    "L": [ml_rule17,],
    "M": [ml_rule17,],
    "N": [ml_rule17,],
    "O": [ml_rule17,],
    "P": [ml_rule17,],
    "Q": [ml_rule17,],
    "R": [ml_rule17,],
    "S": [ml_rule17,],
    "T": [ml_rule17,],
    "U": [ml_rule17,],
    "V": [ml_rule17,],
    "W": [ml_rule17,],
    "X": [ml_rule17,],
    "Y": [ml_rule17,],
    "Z": [ml_rule17,],
    "^": [ml_rule7,],
    "a": [ml_rule17,],
    "b": [ml_rule17,],
    "c": [ml_rule17,],
    "d": [ml_rule17,],
    "e": [ml_rule17,],
    "f": [ml_rule17,],
    "g": [ml_rule17,],
    "h": [ml_rule17,],
    "i": [ml_rule17,],
    "j": [ml_rule17,],
    "k": [ml_rule17,],
    "l": [ml_rule17,],
    "m": [ml_rule17,],
    "n": [ml_rule17,],
    "o": [ml_rule17,],
    "p": [ml_rule17,],
    "q": [ml_rule17,],
    "r": [ml_rule17,],
    "s": [ml_rule17,],
    "t": [ml_rule17,],
    "u": [ml_rule17,],
    "v": [ml_rule17,],
    "w": [ml_rule17,],
    "x": [ml_rule17,],
    "y": [ml_rule17,],
    "z": [ml_rule17,],
}

# x.rulesDictDict for ml mode.
rulesDictDict = {
    "ml_main": rulesDict1,
}

# Import dict for ml mode.
importDict = {}
