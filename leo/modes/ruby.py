# Leo colorizer control file for ruby mode.
# This file is in the public domain.

# Properties for ruby mode.
properties = {
    "commentEnd": "=end",
    "commentStart": "=begin",
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "#",
    "lineUpClosingBracket": "true",
}

# Attributes dict for ruby_main ruleset.
ruby_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for ruby_doublequoteliteral ruleset.
ruby_doublequoteliteral_attributes_dict = {
    "default": "LITERAL1",
        # Fix https://github.com/leo-editor/leo-editor/issues/47
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for ruby mode.
attributesDictDict = {
    "ruby_doublequoteliteral": ruby_doublequoteliteral_attributes_dict,
    "ruby_main": ruby_main_attributes_dict,
}

# Keywords dict for ruby_main ruleset.
ruby_main_keywords_dict = {
    "BEGIN": "keyword1",
    "END": "keyword1",
    "__FILE__": "literal2",
    "__LINE__": "literal2",
    "alias": "keyword1",
    "and": "keyword1",
    "begin": "keyword1",
    "break": "keyword1",
    "case": "keyword1",
    "class": "keyword1",
    "def": "keyword1",
    "defined": "keyword1",
    "do": "keyword1",
    "else": "keyword1",
    "elsif": "keyword1",
    "end": "keyword1",
    "ensure": "keyword1",
    "false": "literal2",
    "for": "keyword1",
    "if": "keyword1",
    "in": "keyword1",
    "include": "keyword2",
    "module": "keyword1",
    "next": "keyword1",
    "nil": "keyword1",
    "not": "operator",
    "or": "keyword1",
    "redo": "keyword1",
    "require": "keyword2",
    "rescue": "keyword1",
    "retry": "keyword1",
    "return": "keyword1",
    "self": "literal2",
    "super": "literal2",
    "then": "keyword1",
    "true": "literal2",
    "undef": "keyword1",
    "unless": "keyword1",
    "until": "keyword1",
    "when": "keyword1",
    "while": "keyword1",
    "yield": "keyword1",
}

# Keywords dict for ruby_doublequoteliteral ruleset.
ruby_doublequoteliteral_keywords_dict = {}

# Dictionary of keywords dictionaries for ruby mode.
keywordsDictDict = {
    "ruby_doublequoteliteral": ruby_doublequoteliteral_keywords_dict,
    "ruby_main": ruby_main_keywords_dict,
}

# Rules for ruby_main ruleset.

def ruby_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="=begin", end="=end")

def ruby_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="#{", end="}",
          exclude_match=True)

def ruby_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="ruby::doublequoteliteral",
          no_line_break=True)

def ruby_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def ruby_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def ruby_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def ruby_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def ruby_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def ruby_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def ruby_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="::")

def ruby_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="===")

def ruby_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def ruby_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>")

def ruby_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<<")

def ruby_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def ruby_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def ruby_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def ruby_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def ruby_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="**")

def ruby_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def ruby_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def ruby_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def ruby_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def ruby_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def ruby_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def ruby_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def ruby_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def ruby_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def ruby_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="...")

def ruby_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="..")

def ruby_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def ruby_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def ruby_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def ruby_rule33(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def ruby_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def ruby_rule35(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for ruby_main ruleset.
rulesDict1 = {
    "!": [ruby_rule23,],
    "\"": [ruby_rule2,],
    "#": [ruby_rule1, ruby_rule4,],
    "%": [ruby_rule20,],
    "&": [ruby_rule21,],
    "'": [ruby_rule3,],
    "(": [ruby_rule7,],
    ")": [ruby_rule8,],
    "*": [ruby_rule18, ruby_rule19,],
    "+": [ruby_rule15,],
    "-": [ruby_rule16,],
    ".": [ruby_rule28, ruby_rule29,],
    "/": [ruby_rule17,],
    "0": [ruby_rule35,],
    "1": [ruby_rule35,],
    "2": [ruby_rule35,],
    "3": [ruby_rule35,],
    "4": [ruby_rule35,],
    "5": [ruby_rule35,],
    "6": [ruby_rule35,],
    "7": [ruby_rule35,],
    "8": [ruby_rule35,],
    "9": [ruby_rule35,],
    ":": [ruby_rule9, ruby_rule33, ruby_rule34,],
    "<": [ruby_rule13, ruby_rule14, ruby_rule25,],
    "=": [ruby_rule0, ruby_rule10, ruby_rule11,],
    ">": [ruby_rule12, ruby_rule24,],
    "?": [ruby_rule32,],
    "@": [ruby_rule35,],
    "A": [ruby_rule35,],
    "B": [ruby_rule35,],
    "C": [ruby_rule35,],
    "D": [ruby_rule35,],
    "E": [ruby_rule35,],
    "F": [ruby_rule35,],
    "G": [ruby_rule35,],
    "H": [ruby_rule35,],
    "I": [ruby_rule35,],
    "J": [ruby_rule35,],
    "K": [ruby_rule35,],
    "L": [ruby_rule35,],
    "M": [ruby_rule35,],
    "N": [ruby_rule35,],
    "O": [ruby_rule35,],
    "P": [ruby_rule35,],
    "Q": [ruby_rule35,],
    "R": [ruby_rule35,],
    "S": [ruby_rule35,],
    "T": [ruby_rule35,],
    "U": [ruby_rule35,],
    "V": [ruby_rule35,],
    "W": [ruby_rule35,],
    "X": [ruby_rule35,],
    "Y": [ruby_rule35,],
    "Z": [ruby_rule35,],
    "[": [ruby_rule31,],
    "]": [ruby_rule30,],
    "^": [ruby_rule26,],
    "_": [ruby_rule35,],
    "a": [ruby_rule35,],
    "b": [ruby_rule35,],
    "c": [ruby_rule35,],
    "d": [ruby_rule35,],
    "e": [ruby_rule35,],
    "f": [ruby_rule35,],
    "g": [ruby_rule35,],
    "h": [ruby_rule35,],
    "i": [ruby_rule35,],
    "j": [ruby_rule35,],
    "k": [ruby_rule35,],
    "l": [ruby_rule35,],
    "m": [ruby_rule35,],
    "n": [ruby_rule35,],
    "o": [ruby_rule35,],
    "p": [ruby_rule35,],
    "q": [ruby_rule35,],
    "r": [ruby_rule35,],
    "s": [ruby_rule35,],
    "t": [ruby_rule35,],
    "u": [ruby_rule35,],
    "v": [ruby_rule35,],
    "w": [ruby_rule35,],
    "x": [ruby_rule35,],
    "y": [ruby_rule35,],
    "z": [ruby_rule35,],
    "{": [ruby_rule5,],
    "|": [ruby_rule22,],
    "}": [ruby_rule6,],
    "~": [ruby_rule27,],
}

# Rules for ruby_doublequoteliteral ruleset.

def ruby_rule36(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="#{", end="}",
          exclude_match=True)

# Rules dict for ruby_doublequoteliteral ruleset.
rulesDict2 = {
    "#": [ruby_rule36,],
}

# x.rulesDictDict for ruby mode.
rulesDictDict = {
    "ruby_doublequoteliteral": rulesDict2,
    "ruby_main": rulesDict1,
}

# Import dict for ruby mode.
importDict = {}
