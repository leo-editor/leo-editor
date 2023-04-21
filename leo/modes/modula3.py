# Leo colorizer control file for modula3 mode.
# This file is in the public domain.

# Properties for modula3 mode.
properties = {
    "commentEnd": "*)",
    "commentStart": "(*",
}

# Attributes dict for modula3_main ruleset.
modula3_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for modula3 mode.
attributesDictDict = {
    "modula3_main": modula3_main_attributes_dict,
}

# Keywords dict for modula3_main ruleset.
modula3_main_keywords_dict = {
    "abs": "literal2",
    "address": "literal2",
    "adr": "literal2",
    "adrsize": "literal2",
    "and": "keyword1",
    "any": "keyword1",
    "array": "keyword1",
    "as": "keyword1",
    "begin": "keyword1",
    "bits": "keyword1",
    "bitsize": "literal2",
    "boolean": "literal2",
    "branded": "keyword1",
    "by": "keyword1",
    "bytesize": "literal2",
    "cardinal": "literal2",
    "case": "keyword1",
    "ceiling": "literal2",
    "char": "literal2",
    "const": "keyword1",
    "dec": "literal2",
    "dispose": "literal2",
    "div": "keyword1",
    "do": "keyword1",
    "else": "keyword1",
    "elsif": "keyword1",
    "end": "keyword1",
    "eval": "keyword1",
    "except": "keyword1",
    "exception": "keyword1",
    "exit": "keyword1",
    "exports": "keyword1",
    "extended": "literal2",
    "extendedfloat": "keyword2",
    "extendedreal": "keyword2",
    "false": "literal2",
    "finally": "keyword1",
    "first": "literal2",
    "float": "literal2",
    "floatmode": "keyword2",
    "floor": "literal2",
    "fmt": "keyword3",
    "for": "keyword1",
    "from": "keyword1",
    "generic": "keyword1",
    "if": "keyword1",
    "import": "keyword1",
    "in": "keyword1",
    "inc": "literal2",
    "integer": "literal2",
    "interface": "keyword1",
    "istype": "literal2",
    "last": "literal2",
    "lex": "keyword3",
    "lock": "keyword1",
    "longfloat": "keyword2",
    "longreal": "literal2",
    "loop": "keyword1",
    "loophole": "literal2",
    "max": "literal2",
    "methods": "keyword1",
    "min": "literal2",
    "mod": "keyword1",
    "module": "keyword1",
    "mutex": "literal2",
    "narrow": "literal2",
    "new": "literal2",
    "nil": "literal2",
    "not": "keyword1",
    "null": "literal2",
    "number": "literal2",
    "object": "keyword1",
    "of": "keyword1",
    "or": "keyword1",
    "ord": "literal2",
    "overrides": "keyword1",
    "pickle": "keyword3",
    "procedure": "keyword1",
    "raise": "keyword1",
    "raises": "keyword1",
    "readonly": "keyword1",
    "real": "keyword2",
    "realfloat": "keyword2",
    "record": "keyword1",
    "ref": "keyword1",
    "refany": "literal2",
    "repeat": "keyword1",
    "return": "keyword1",
    "reveal": "keyword1",
    "root": "keyword1",
    "round": "literal2",
    "set": "keyword1",
    "subarray": "literal2",
    "table": "keyword3",
    "text": "keyword2",
    "then": "keyword1",
    "thread": "keyword2",
    "to": "keyword1",
    "true": "literal2",
    "trunc": "literal2",
    "try": "keyword1",
    "type": "keyword1",
    "typecase": "keyword1",
    "typecode": "literal2",
    "unsafe": "keyword1",
    "until": "keyword1",
    "untraced": "keyword1",
    "val": "literal2",
    "value": "keyword1",
    "var": "keyword1",
    "while": "keyword1",
    "with": "keyword1",
    "word": "keyword2",
}

# Dictionary of keywords dictionaries for modula3 mode.
keywordsDictDict = {
    "modula3_main": modula3_main_keywords_dict,
}

# Rules for modula3_main ruleset.

def modula3_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="<*", end="*>")

def modula3_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="(*", end="*)")

def modula3_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def modula3_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def modula3_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def modula3_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def modula3_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def modula3_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def modula3_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<>")

def modula3_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def modula3_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def modula3_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def modula3_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def modula3_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def modula3_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def modula3_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def modula3_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def modula3_rule17(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for modula3_main ruleset.
rulesDict1 = {
    "\"": [modula3_rule2,],
    "'": [modula3_rule3,],
    "(": [modula3_rule1,],
    "*": [modula3_rule16,],
    "+": [modula3_rule13,],
    "-": [modula3_rule14,],
    "/": [modula3_rule15,],
    "0": [modula3_rule17,],
    "1": [modula3_rule17,],
    "2": [modula3_rule17,],
    "3": [modula3_rule17,],
    "4": [modula3_rule17,],
    "5": [modula3_rule17,],
    "6": [modula3_rule17,],
    "7": [modula3_rule17,],
    "8": [modula3_rule17,],
    "9": [modula3_rule17,],
    ":": [modula3_rule6,],
    "<": [modula3_rule0, modula3_rule8, modula3_rule10, modula3_rule12,],
    "=": [modula3_rule7,],
    ">": [modula3_rule9, modula3_rule11,],
    "@": [modula3_rule5, modula3_rule17,],
    "A": [modula3_rule17,],
    "B": [modula3_rule17,],
    "C": [modula3_rule17,],
    "D": [modula3_rule17,],
    "E": [modula3_rule17,],
    "F": [modula3_rule17,],
    "G": [modula3_rule17,],
    "H": [modula3_rule17,],
    "I": [modula3_rule17,],
    "J": [modula3_rule17,],
    "K": [modula3_rule17,],
    "L": [modula3_rule17,],
    "M": [modula3_rule17,],
    "N": [modula3_rule17,],
    "O": [modula3_rule17,],
    "P": [modula3_rule17,],
    "Q": [modula3_rule17,],
    "R": [modula3_rule17,],
    "S": [modula3_rule17,],
    "T": [modula3_rule17,],
    "U": [modula3_rule17,],
    "V": [modula3_rule17,],
    "W": [modula3_rule17,],
    "X": [modula3_rule17,],
    "Y": [modula3_rule17,],
    "Z": [modula3_rule17,],
    "^": [modula3_rule4,],
    "a": [modula3_rule17,],
    "b": [modula3_rule17,],
    "c": [modula3_rule17,],
    "d": [modula3_rule17,],
    "e": [modula3_rule17,],
    "f": [modula3_rule17,],
    "g": [modula3_rule17,],
    "h": [modula3_rule17,],
    "i": [modula3_rule17,],
    "j": [modula3_rule17,],
    "k": [modula3_rule17,],
    "l": [modula3_rule17,],
    "m": [modula3_rule17,],
    "n": [modula3_rule17,],
    "o": [modula3_rule17,],
    "p": [modula3_rule17,],
    "q": [modula3_rule17,],
    "r": [modula3_rule17,],
    "s": [modula3_rule17,],
    "t": [modula3_rule17,],
    "u": [modula3_rule17,],
    "v": [modula3_rule17,],
    "w": [modula3_rule17,],
    "x": [modula3_rule17,],
    "y": [modula3_rule17,],
    "z": [modula3_rule17,],
}

# x.rulesDictDict for modula3 mode.
rulesDictDict = {
    "modula3_main": rulesDict1,
}

# Import dict for modula3 mode.
importDict = {}
