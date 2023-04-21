# Leo colorizer control file for vhdl mode.
# This file is in the public domain.

# Properties for vhdl mode.
properties = {
    "label": "VHDL",
    "lineComment": "--",
}

# Attributes dict for vhdl_main ruleset.
vhdl_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for vhdl mode.
attributesDictDict = {
    "vhdl_main": vhdl_main_attributes_dict,
}

# Keywords dict for vhdl_main ruleset.
vhdl_main_keywords_dict = {
    "abs": "operator",
    "active": "keyword3",
    "alias": "keyword1",
    "all": "keyword1",
    "and": "operator",
    "architecture": "keyword1",
    "array": "keyword1",
    "ascending": "keyword3",
    "assert": "keyword1",
    "base": "keyword3",
    "begin": "keyword1",
    "bit": "keyword2",
    "bit_vector": "keyword2",
    "break": "keyword1",
    "case": "keyword1",
    "catch": "keyword1",
    "component": "keyword1",
    "constant": "keyword1",
    "continue": "keyword1",
    "default": "keyword1",
    "delayed": "keyword3",
    "do": "keyword1",
    "downto": "keyword1",
    "driving": "keyword3",
    "else": "keyword1",
    "elsif": "keyword1",
    "end": "keyword1",
    "entity": "keyword1",
    "event": "keyword3",
    "extends": "keyword1",
    "false": "literal2",
    "for": "keyword1",
    "function": "keyword1",
    "generic": "keyword1",
    "high": "keyword3",
    "if": "keyword1",
    "image": "keyword3",
    "implements": "keyword1",
    "import": "keyword2",
    "in": "keyword1",
    "inout": "keyword1",
    "instance": "keyword3",
    "instanceof": "keyword1",
    "integer": "keyword2",
    "is": "keyword1",
    "last": "keyword3",
    "left": "keyword3",
    "leftof": "keyword3",
    "length": "keyword3",
    "library": "keyword1",
    "loop": "keyword1",
    "low": "keyword3",
    "mod": "operator",
    "nand": "operator",
    "natural": "keyword2",
    "nor": "operator",
    "not": "operator",
    "of": "keyword1",
    "or": "operator",
    "others": "keyword1",
    "out": "keyword1",
    "package": "keyword2",
    "path": "keyword3",
    "port": "keyword1",
    "pos": "keyword3",
    "pred": "keyword3",
    "process": "keyword1",
    "quiet": "keyword3",
    "range": "keyword3",
    "record": "keyword1",
    "rem": "operator",
    "resize": "function",
    "return": "keyword1",
    "reverse": "keyword3",
    "right": "keyword3",
    "rightof": "keyword3",
    "rising_edge": "function",
    "rol": "operator",
    "ror": "operator",
    "rotate_left": "function",
    "rotate_right": "function",
    "shift_left": "function",
    "shift_right": "function",
    "signal": "keyword1",
    "signed": "function",
    "simple": "keyword3",
    "sla": "operator",
    "sll": "operator",
    "sra": "operator",
    "srl": "operator",
    "stable": "keyword3",
    "static": "keyword1",
    "std_logic": "keyword2",
    "std_logic_vector": "keyword2",
    "std_match": "function",
    "std_ulogic": "keyword2",
    "std_ulogic_vector": "keyword2",
    "succ": "keyword3",
    "switch": "keyword1",
    "then": "keyword1",
    "to": "keyword1",
    "to_bit": "function",
    "to_bitvector": "function",
    "to_integer": "function",
    "to_signed": "function",
    "to_stdlogicvector": "function",
    "to_stdulogic": "function",
    "to_stdulogicvector": "function",
    "to_unsigned": "function",
    "transaction": "keyword3",
    "true": "literal2",
    "type": "keyword1",
    "unsigned": "function",
    "upto": "keyword1",
    "use": "keyword1",
    "val": "keyword3",
    "value": "keyword3",
    "variable": "keyword1",
    "wait": "keyword1",
    "when": "keyword1",
    "while": "keyword1",
    "xnor": "operator",
}

# Dictionary of keywords dictionaries for vhdl mode.
keywordsDictDict = {
    "vhdl_main": vhdl_main_keywords_dict,
}

# Rules for vhdl_main ruleset.

def vhdl_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def vhdl_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="'event")

def vhdl_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def vhdl_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def vhdl_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def vhdl_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/=")

def vhdl_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def vhdl_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def vhdl_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def vhdl_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def vhdl_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def vhdl_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def vhdl_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def vhdl_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def vhdl_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def vhdl_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def vhdl_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="**")

def vhdl_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def vhdl_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def vhdl_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def vhdl_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def vhdl_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def vhdl_rule22(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          exclude_match=True)

def vhdl_rule23(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for vhdl_main ruleset.
rulesDict1 = {
    "!": [vhdl_rule6,],
    "\"": [vhdl_rule0,],
    "%": [vhdl_rule17,],
    "&": [vhdl_rule18,],
    "'": [vhdl_rule1, vhdl_rule2,],
    "*": [vhdl_rule15, vhdl_rule16,],
    "+": [vhdl_rule12,],
    "-": [vhdl_rule3, vhdl_rule13,],
    "/": [vhdl_rule5, vhdl_rule14,],
    "0": [vhdl_rule23,],
    "1": [vhdl_rule23,],
    "2": [vhdl_rule23,],
    "3": [vhdl_rule23,],
    "4": [vhdl_rule23,],
    "5": [vhdl_rule23,],
    "6": [vhdl_rule23,],
    "7": [vhdl_rule23,],
    "8": [vhdl_rule23,],
    "9": [vhdl_rule23,],
    ":": [vhdl_rule7, vhdl_rule22,],
    "<": [vhdl_rule10, vhdl_rule11,],
    "=": [vhdl_rule4,],
    ">": [vhdl_rule8, vhdl_rule9,],
    "@": [vhdl_rule23,],
    "A": [vhdl_rule23,],
    "B": [vhdl_rule23,],
    "C": [vhdl_rule23,],
    "D": [vhdl_rule23,],
    "E": [vhdl_rule23,],
    "F": [vhdl_rule23,],
    "G": [vhdl_rule23,],
    "H": [vhdl_rule23,],
    "I": [vhdl_rule23,],
    "J": [vhdl_rule23,],
    "K": [vhdl_rule23,],
    "L": [vhdl_rule23,],
    "M": [vhdl_rule23,],
    "N": [vhdl_rule23,],
    "O": [vhdl_rule23,],
    "P": [vhdl_rule23,],
    "Q": [vhdl_rule23,],
    "R": [vhdl_rule23,],
    "S": [vhdl_rule23,],
    "T": [vhdl_rule23,],
    "U": [vhdl_rule23,],
    "V": [vhdl_rule23,],
    "W": [vhdl_rule23,],
    "X": [vhdl_rule23,],
    "Y": [vhdl_rule23,],
    "Z": [vhdl_rule23,],
    "^": [vhdl_rule20,],
    "_": [vhdl_rule23,],
    "a": [vhdl_rule23,],
    "b": [vhdl_rule23,],
    "c": [vhdl_rule23,],
    "d": [vhdl_rule23,],
    "e": [vhdl_rule23,],
    "f": [vhdl_rule23,],
    "g": [vhdl_rule23,],
    "h": [vhdl_rule23,],
    "i": [vhdl_rule23,],
    "j": [vhdl_rule23,],
    "k": [vhdl_rule23,],
    "l": [vhdl_rule23,],
    "m": [vhdl_rule23,],
    "n": [vhdl_rule23,],
    "o": [vhdl_rule23,],
    "p": [vhdl_rule23,],
    "q": [vhdl_rule23,],
    "r": [vhdl_rule23,],
    "s": [vhdl_rule23,],
    "t": [vhdl_rule23,],
    "u": [vhdl_rule23,],
    "v": [vhdl_rule23,],
    "w": [vhdl_rule23,],
    "x": [vhdl_rule23,],
    "y": [vhdl_rule23,],
    "z": [vhdl_rule23,],
    "|": [vhdl_rule19,],
    "~": [vhdl_rule21,],
}

# x.rulesDictDict for vhdl mode.
rulesDictDict = {
    "vhdl_main": rulesDict1,
}

# Import dict for vhdl mode.
importDict = {}
