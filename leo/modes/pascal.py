# Leo colorizer control file for pascal mode.
# This file is in the public domain.

# Properties for pascal mode.
properties = {
    "commentEnd": "}",
    "commentStart": "{",
    "lineComment": "//",
}

# Attributes dict for pascal_main ruleset.
pascal_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for pascal mode.
attributesDictDict = {
    "pascal_main": pascal_main_attributes_dict,
}

# Keywords dict for pascal_main ruleset.
pascal_main_keywords_dict = {
    "absolute": "keyword2",
    "abstract": "keyword2",
    "and": "keyword1",
    "array": "keyword1",
    "as": "keyword1",
    "asm": "keyword1",
    "assembler": "keyword2",
    "at": "keyword1",
    "automated": "keyword2",
    "begin": "keyword1",
    "boolean": "keyword3",
    "byte": "keyword3",
    "bytebool": "keyword3",
    "cardinal": "keyword3",
    "case": "keyword1",
    "cdecl": "keyword2",
    "char": "keyword3",
    "class": "keyword1",
    "comp": "keyword3",
    "const": "keyword1",
    "constructor": "keyword1",
    "contains": "keyword2",
    "currency": "keyword3",
    "default": "keyword2",
    "deprecated": "keyword2",
    "destructor": "keyword1",
    "dispid": "keyword2",
    "dispinterface": "keyword1",
    "div": "keyword1",
    "do": "keyword1",
    "double": "keyword3",
    "downto": "keyword1",
    "dynamic": "keyword2",
    "else": "keyword1",
    "end": "keyword1",
    "except": "keyword1",
    "export": "keyword2",
    "exports": "keyword1",
    "extended": "keyword3",
    "external": "keyword2",
    "false": "literal2",
    "far": "keyword2",
    "file": "keyword1",
    "final": "keyword1",
    "finalization": "keyword1",
    "finally": "keyword1",
    "for": "keyword1",
    "forward": "keyword2",
    "function": "keyword1",
    "goto": "keyword1",
    "if": "keyword1",
    "implementation": "keyword1",
    "implements": "keyword2",
    "in": "keyword1",
    "index": "keyword2",
    "inherited": "keyword1",
    "initialization": "keyword1",
    "inline": "keyword1",
    "integer": "keyword3",
    "interface": "keyword1",
    "is": "keyword1",
    "label": "keyword1",
    "library": "keyword2",
    "local": "keyword2",
    "longbool": "keyword3",
    "longint": "keyword3",
    "message": "keyword2",
    "mod": "keyword1",
    "name": "keyword2",
    "namespaces": "keyword2",
    "near": "keyword2",
    "nil": "literal2",
    "nodefault": "keyword2",
    "not": "keyword1",
    "object": "keyword1",
    "of": "keyword1",
    "on": "keyword1",
    "or": "keyword1",
    "out": "keyword1",
    "overload": "keyword2",
    "override": "keyword2",
    "package": "keyword2",
    "packed": "keyword1",
    "pascal": "keyword2",
    "platform": "keyword2",
    "pointer": "keyword3",
    "private": "keyword2",
    "procedure": "keyword1",
    "program": "keyword1",
    "property": "keyword1",
    "protected": "keyword2",
    "public": "keyword2",
    "published": "keyword2",
    "raise": "keyword1",
    "read": "keyword2",
    "readonly": "keyword2",
    "real": "keyword3",
    "record": "keyword1",
    "register": "keyword2",
    "reintroduce": "keyword2",
    "repeat": "keyword1",
    "requires": "keyword2",
    "resident": "keyword2",
    "resourcestring": "keyword1",
    "safecall": "keyword2",
    "sealed": "keyword1",
    "self": "literal2",
    "set": "keyword1",
    "shl": "keyword1",
    "shortint": "keyword3",
    "shr": "keyword1",
    "single": "keyword3",
    "smallint": "keyword3",
    "static": "keyword1",
    "stdcall": "keyword2",
    "stored": "keyword2",
    "string": "keyword1",
    "then": "keyword1",
    "threadvar": "keyword1",
    "to": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "type": "keyword1",
    "unit": "keyword1",
    "unsafe": "keyword1",
    "until": "keyword1",
    "uses": "keyword1",
    "var": "keyword1",
    "varargs": "keyword2",
    "virtual": "keyword2",
    "while": "keyword1",
    "with": "keyword1",
    "word": "keyword3",
    "wordbool": "keyword3",
    "write": "keyword2",
    "writeonly": "keyword2",
    "xor": "keyword1",
}

# Dictionary of keywords dictionaries for pascal mode.
keywordsDictDict = {
    "pascal_main": pascal_main_keywords_dict,
}

# Rules for pascal_main ruleset.

def pascal_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="{$", end="}")

def pascal_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="(*$", end="*)")

def pascal_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="{", end="}")

def pascal_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="(*", end="*)")

def pascal_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def pascal_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def pascal_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def pascal_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def pascal_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def pascal_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def pascal_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def pascal_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def pascal_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def pascal_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def pascal_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def pascal_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def pascal_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def pascal_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def pascal_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<>")

def pascal_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def pascal_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def pascal_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def pascal_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def pascal_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def pascal_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def pascal_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def pascal_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def pascal_rule27(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for pascal_main ruleset.
rulesDict1 = {
    "'": [pascal_rule5,],
    "(": [pascal_rule1, pascal_rule3, pascal_rule7,],
    ")": [pascal_rule6,],
    "*": [pascal_rule26,],
    "+": [pascal_rule23,],
    ",": [pascal_rule11,],
    "-": [pascal_rule24,],
    ".": [pascal_rule10,],
    "/": [pascal_rule4, pascal_rule25,],
    "0": [pascal_rule27,],
    "1": [pascal_rule27,],
    "2": [pascal_rule27,],
    "3": [pascal_rule27,],
    "4": [pascal_rule27,],
    "5": [pascal_rule27,],
    "6": [pascal_rule27,],
    "7": [pascal_rule27,],
    "8": [pascal_rule27,],
    "9": [pascal_rule27,],
    ":": [pascal_rule15, pascal_rule16,],
    ";": [pascal_rule12,],
    "<": [pascal_rule18, pascal_rule20, pascal_rule22,],
    "=": [pascal_rule17,],
    ">": [pascal_rule19, pascal_rule21,],
    "@": [pascal_rule14, pascal_rule27,],
    "A": [pascal_rule27,],
    "B": [pascal_rule27,],
    "C": [pascal_rule27,],
    "D": [pascal_rule27,],
    "E": [pascal_rule27,],
    "F": [pascal_rule27,],
    "G": [pascal_rule27,],
    "H": [pascal_rule27,],
    "I": [pascal_rule27,],
    "J": [pascal_rule27,],
    "K": [pascal_rule27,],
    "L": [pascal_rule27,],
    "M": [pascal_rule27,],
    "N": [pascal_rule27,],
    "O": [pascal_rule27,],
    "P": [pascal_rule27,],
    "Q": [pascal_rule27,],
    "R": [pascal_rule27,],
    "S": [pascal_rule27,],
    "T": [pascal_rule27,],
    "U": [pascal_rule27,],
    "V": [pascal_rule27,],
    "W": [pascal_rule27,],
    "X": [pascal_rule27,],
    "Y": [pascal_rule27,],
    "Z": [pascal_rule27,],
    "[": [pascal_rule9,],
    "]": [pascal_rule8,],
    "^": [pascal_rule13,],
    "a": [pascal_rule27,],
    "b": [pascal_rule27,],
    "c": [pascal_rule27,],
    "d": [pascal_rule27,],
    "e": [pascal_rule27,],
    "f": [pascal_rule27,],
    "g": [pascal_rule27,],
    "h": [pascal_rule27,],
    "i": [pascal_rule27,],
    "j": [pascal_rule27,],
    "k": [pascal_rule27,],
    "l": [pascal_rule27,],
    "m": [pascal_rule27,],
    "n": [pascal_rule27,],
    "o": [pascal_rule27,],
    "p": [pascal_rule27,],
    "q": [pascal_rule27,],
    "r": [pascal_rule27,],
    "s": [pascal_rule27,],
    "t": [pascal_rule27,],
    "u": [pascal_rule27,],
    "v": [pascal_rule27,],
    "w": [pascal_rule27,],
    "x": [pascal_rule27,],
    "y": [pascal_rule27,],
    "z": [pascal_rule27,],
    "{": [pascal_rule0, pascal_rule2,],
}

# x.rulesDictDict for pascal mode.
rulesDictDict = {
    "pascal_main": rulesDict1,
}

# Import dict for pascal mode.
importDict = {}
