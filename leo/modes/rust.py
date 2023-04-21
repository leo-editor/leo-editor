# Leo colorizer control file for rust mode.
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
rust_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]_]+[lL]?|[[:digit:]_]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for c mode.
attributesDictDict = {
    "rust_main": rust_main_attributes_dict,
}

# Keywords dict for c_main ruleset.
rust_main_keywords_dict = {
    'Self': 'keyword1',
    'abstract': 'keyword1',
    'as': 'keyword1',
    'async': 'keyword1',
    'become': 'keyword1',
    'box': 'keyword1',
    'break': 'keyword1',
    'const': 'keyword1',
    'continue': 'keyword1',
    'crate': 'keyword1',
    'do': 'keyword1',
    'dyn': 'keyword1',
    'else': 'keyword1',
    'enum': 'keyword1',
    'extern': 'keyword1',
    'false': 'keyword1',
    'final': 'keyword1',
    'fn': 'keyword1',
    'for': 'keyword1',
    'i16': 'keyword2',
    'i32': 'keyword2',
    'i64': 'keyword2',
    'i8': 'keyword2',
    'if': 'keyword1',
    'impl': 'keyword1',
    'in': 'keyword1',
    'let': 'keyword1',
    'loop': 'keyword1',
    'macro': 'keyword1',
    'match': 'keyword1',
    'mod': 'keyword1',
    'move': 'keyword1',
    'mut': 'keyword1',
    'override': 'keyword1',
    'priv': 'keyword1',
    'pub': 'keyword1',
    'ref': 'keyword1',
    'return': 'keyword1',
    'self': 'keyword1',
    'static': 'keyword1',
    'str': 'keyword2',
    'struct': 'keyword1',
    'super': 'keyword1',
    'trait': 'keyword1',
    'true': 'keyword1',
    'try': 'keyword1',
    'type': 'keyword1',
    'typeof': 'keyword1',
    'u16': 'keyword2',
    'u32': 'keyword2',
    'u64': 'keyword2',
    'u8': 'keyword2',
    'unsafe': 'keyword1',
    'unsized': 'keyword1',
    'use': 'keyword1',
    'usize': 'keyword2',
    'vec!': 'keyword2',
    'virtual': 'keyword1',
    'where': 'keyword1',
    'while': 'keyword1',
    'yield': 'keyword1',
    'Some': 'keyword3',
    'None': 'keyword3',
    'Result': 'keyword3',
    'Err': 'keyword3',
    'Ok': 'keyword3',
    'include_bytes': 'keyword2',
    'include_str': 'keyword2',
}


# Dictionary of keywords dictionaries for c mode.
keywordsDictDict = {
    "rust_main": rust_main_keywords_dict,
}

# Rules for rust_main ruleset.

def rust_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="doxygen::doxygen")

def rust_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/*!", end="*/",
          delegate="doxygen::doxygen")

def rust_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def rust_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"", end="\"")

def rust_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="'", end="'",
          no_line_break=True)

def rust_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="##")

def rust_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#")

def rust_rule7(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def rust_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def rust_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def rust_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def rust_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def rust_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def rust_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def rust_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def rust_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def rust_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def rust_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def rust_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def rust_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def rust_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def rust_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def rust_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def rust_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def rust_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def rust_rule25(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def rust_rule26(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def rust_rule27(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for c_main ruleset.
rulesDict1 = {
    "!": [rust_rule9,],
    "\"": [rust_rule3,],
    "#": [rust_rule5, rust_rule6,],
    "%": [rust_rule18,],
    "&": [rust_rule19,],
    "'": [rust_rule4,],
    "(": [rust_rule26,],
    "*": [rust_rule15,],
    "+": [rust_rule12,],
    "-": [rust_rule13,],
    "/": [rust_rule0, rust_rule1, rust_rule2, rust_rule7, rust_rule14,],
    "0": [rust_rule27,],
    "1": [rust_rule27,],
    "2": [rust_rule27,],
    "3": [rust_rule27,],
    "4": [rust_rule27,],
    "5": [rust_rule27,],
    "6": [rust_rule27,],
    "7": [rust_rule27,],
    "8": [rust_rule27,],
    "9": [rust_rule27,],
    ":": [rust_rule25,],
    "<": [rust_rule11, rust_rule17,],
    "=": [rust_rule8,],
    ">": [rust_rule10, rust_rule16,],
    "@": [rust_rule27,],
    "A": [rust_rule27,],
    "B": [rust_rule27,],
    "C": [rust_rule27,],
    "D": [rust_rule27,],
    "E": [rust_rule27,],
    "F": [rust_rule27,],
    "G": [rust_rule27,],
    "H": [rust_rule27,],
    "I": [rust_rule27,],
    "J": [rust_rule27,],
    "K": [rust_rule27,],
    "L": [rust_rule27,],
    "M": [rust_rule27,],
    "N": [rust_rule27,],
    "O": [rust_rule27,],
    "P": [rust_rule27,],
    "Q": [rust_rule27,],
    "R": [rust_rule27,],
    "S": [rust_rule27,],
    "T": [rust_rule27,],
    "U": [rust_rule27,],
    "V": [rust_rule27,],
    "W": [rust_rule27,],
    "X": [rust_rule27,],
    "Y": [rust_rule27,],
    "Z": [rust_rule27,],
    "^": [rust_rule21,],
    "_": [rust_rule27,],
    "a": [rust_rule27,],
    "b": [rust_rule27,],
    "c": [rust_rule27,],
    "d": [rust_rule27,],
    "e": [rust_rule27,],
    "f": [rust_rule27,],
    "g": [rust_rule27,],
    "h": [rust_rule27,],
    "i": [rust_rule27,],
    "j": [rust_rule27,],
    "k": [rust_rule27,],
    "l": [rust_rule27,],
    "m": [rust_rule27,],
    "n": [rust_rule27,],
    "o": [rust_rule27,],
    "p": [rust_rule27,],
    "q": [rust_rule27,],
    "r": [rust_rule27,],
    "s": [rust_rule27,],
    "t": [rust_rule27,],
    "u": [rust_rule27,],
    "v": [rust_rule27,],
    "w": [rust_rule27,],
    "x": [rust_rule27,],
    "y": [rust_rule27,],
    "z": [rust_rule27,],
    "{": [rust_rule24,],
    "|": [rust_rule20,],
    "}": [rust_rule23,],
    "~": [rust_rule22,],
}


# x.rulesDictDict for rust mode.
rulesDictDict = {
    "rust_main": rulesDict1,
}

# Import dict for rust mode.
importDict = {}
