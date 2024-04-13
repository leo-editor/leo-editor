# Leo colorizer control file for factor mode.
# This file is in the public domain.

# Properties for factor mode.
properties = {
    "commentEnd": ")",
    "commentStart": "(",
    "doubleBracketIndent": "true",
    "indentCloseBrackets": "]",
    "indentNextLines": "^(\\*<<|:).*",
    "indentOpenBrackets": "[",
    "lineComment": "!",
    "lineUpClosingBracket": "true",
    "noWordSep": "+-*=><;.?/'",
}

# Attributes dict for factor_main ruleset.
factor_main_attributes_dict = {
    "default": "null",
    "digit_re": "-?\\d+([./]\\d+)?",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "+-*=><;.?/'",
}

# Attributes dict for factor_stack_effect ruleset.
factor_stack_effect_attributes_dict = {
    "default": "COMMENT4",
    "digit_re": "-?\\d+([./]\\d+)?",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "+-*=><;.?/'",
}

# Dictionary of attributes dictionaries for factor mode.
attributesDictDict = {
    "factor_main": factor_main_attributes_dict,
    "factor_stack_effect": factor_stack_effect_attributes_dict,
}

# Keywords dict for factor_main ruleset.
factor_main_keywords_dict = {
    "#{": "operator",
    "--": "label",
    ";": "markup",
    "<": "label",
    ">": "label",
    "[": "operator",
    "]": "operator",
    "f": "literal4",
    "r": "keyword1",
    "t": "literal3",
    "{": "operator",
    "|": "operator",
    "}": "operator",
    "~": "label",
}

# Keywords dict for factor_stack_effect ruleset.
factor_stack_effect_keywords_dict = {}

# Dictionary of keywords dictionaries for factor mode.
keywordsDictDict = {
    "factor_main": factor_main_keywords_dict,
    "factor_stack_effect": factor_stack_effect_keywords_dict,
}

# Rules for factor_main ruleset.

def factor_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="#!")

def factor_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="!")

def factor_rule2(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp=":\\s+(\\S+)")

def factor_rule3(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="IN:\\s+(\\S+)")

def factor_rule4(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="USE:\\s+(\\S+)")

def factor_rule5(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="DEFER:\\s+(\\S+)")

def factor_rule6(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="POSTPONE:\\s+(\\S+)")

def factor_rule7(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="CHAR:\\s+(\\S+)")

def factor_rule8(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="BIN:\\s+(\\S+)")

def factor_rule9(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="OCT:\\s+(\\S+)")

def factor_rule10(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="HEX:\\s+(\\S+)")

def factor_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="(", end=")",
          delegate="factor::stack_effect")

def factor_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def factor_rule13(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for factor_main ruleset.
rulesDict1 = {
    "!": [factor_rule1,],
    "\"": [factor_rule12,],
    "#": [factor_rule0, factor_rule13,],
    "(": [factor_rule11,],
    "-": [factor_rule13,],
    "0": [factor_rule13,],
    "1": [factor_rule13,],
    "2": [factor_rule13,],
    "3": [factor_rule13,],
    "4": [factor_rule13,],
    "5": [factor_rule13,],
    "6": [factor_rule13,],
    "7": [factor_rule13,],
    "8": [factor_rule13,],
    "9": [factor_rule13,],
    ":": [factor_rule2,],
    ";": [factor_rule13,],
    "<": [factor_rule13,],
    ">": [factor_rule13,],
    "@": [factor_rule13,],
    "A": [factor_rule13,],
    "B": [factor_rule8, factor_rule13,],
    "C": [factor_rule7, factor_rule13,],
    "D": [factor_rule5, factor_rule13,],
    "E": [factor_rule13,],
    "F": [factor_rule13,],
    "G": [factor_rule13,],
    "H": [factor_rule10, factor_rule13,],
    "I": [factor_rule3, factor_rule13,],
    "J": [factor_rule13,],
    "K": [factor_rule13,],
    "L": [factor_rule13,],
    "M": [factor_rule13,],
    "N": [factor_rule13,],
    "O": [factor_rule9, factor_rule13,],
    "P": [factor_rule6, factor_rule13,],
    "Q": [factor_rule13,],
    "R": [factor_rule13,],
    "S": [factor_rule13,],
    "T": [factor_rule13,],
    "U": [factor_rule4, factor_rule13,],
    "V": [factor_rule13,],
    "W": [factor_rule13,],
    "X": [factor_rule13,],
    "Y": [factor_rule13,],
    "Z": [factor_rule13,],
    "[": [factor_rule13,],
    "]": [factor_rule13,],
    "a": [factor_rule13,],
    "b": [factor_rule13,],
    "c": [factor_rule13,],
    "d": [factor_rule13,],
    "e": [factor_rule13,],
    "f": [factor_rule13,],
    "g": [factor_rule13,],
    "h": [factor_rule13,],
    "i": [factor_rule13,],
    "j": [factor_rule13,],
    "k": [factor_rule13,],
    "l": [factor_rule13,],
    "m": [factor_rule13,],
    "n": [factor_rule13,],
    "o": [factor_rule13,],
    "p": [factor_rule13,],
    "q": [factor_rule13,],
    "r": [factor_rule13,],
    "s": [factor_rule13,],
    "t": [factor_rule13,],
    "u": [factor_rule13,],
    "v": [factor_rule13,],
    "w": [factor_rule13,],
    "x": [factor_rule13,],
    "y": [factor_rule13,],
    "z": [factor_rule13,],
    "{": [factor_rule13,],
    "|": [factor_rule13,],
    "}": [factor_rule13,],
    "~": [factor_rule13,],
}

# Rules for factor_stack_effect ruleset.

def factor_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="--")

# Rules dict for factor_stack_effect ruleset.
rulesDict2 = {
    "-": [factor_rule14,],
}

# x.rulesDictDict for factor mode.
rulesDictDict = {
    "factor_main": rulesDict1,
    "factor_stack_effect": rulesDict2,
}

# Import dict for factor mode.
importDict = {}
