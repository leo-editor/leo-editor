# Leo colorizer control file for sqr mode.
# This file is in the public domain.

# Properties for sqr mode.
properties = {
    "lineComment": "!",
}

# Attributes dict for sqr_main ruleset.
sqr_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for sqr mode.
attributesDictDict = {
    "sqr_main": sqr_main_attributes_dict,
}

# Keywords dict for sqr_main ruleset.
sqr_main_keywords_dict = {
    "add": "keyword2",
    "and": "keyword3",
    "array-add": "keyword2",
    "array-divide": "keyword2",
    "array-multiply": "keyword2",
    "array-subtract": "keyword2",
    "ask": "keyword2",
    "begin-footing": "function",
    "begin-heading": "function",
    "begin-procedure": "function",
    "begin-program": "function",
    "begin-report": "function",
    "begin-select": "keyword1",
    "begin-setup": "function",
    "begin-sql": "keyword1",
    "between": "keyword3",
    "break": "keyword2",
    "call": "keyword2",
    "clear-array": "keyword2",
    "close": "keyword2",
    "columns": "keyword2",
    "commit": "keyword2",
    "concat": "keyword2",
    "connect": "keyword2",
    "create-array": "keyword2",
    "date-time": "keyword2",
    "display": "keyword2",
    "divide": "keyword2",
    "do": "keyword2",
    "dollar-symbol": "keyword2",
    "else": "keyword2",
    "encode": "keyword2",
    "end-evaluate": "keyword2",
    "end-footing": "function",
    "end-heading": "function",
    "end-if": "keyword2",
    "end-procedure": "function",
    "end-program": "function",
    "end-report": "function",
    "end-select": "keyword1",
    "end-setup": "function",
    "end-sql": "keyword1",
    "end-while": "keyword2",
    "evaluate": "keyword2",
    "execute": "keyword2",
    "extract": "keyword2",
    "find": "keyword2",
    "font": "keyword2",
    "from": "keyword3",
    "get": "keyword2",
    "goto": "keyword2",
    "graphic": "keyword2",
    "if": "keyword2",
    "in": "keyword3",
    "last-page": "keyword2",
    "let": "keyword2",
    "lookup": "keyword2",
    "lowercase": "keyword2",
    "money-symbol": "keyword2",
    "move": "keyword2",
    "multiply": "keyword2",
    "new-page": "keyword2",
    "new-report": "keyword2",
    "next-column": "keyword2",
    "next-listing": "keyword2",
    "no-formfeed": "keyword2",
    "open": "keyword2",
    "or": "keyword3",
    "page-number": "keyword2",
    "page-size": "keyword2",
    "position": "keyword2",
    "print": "keyword2",
    "print-bar-code": "keyword2",
    "print-chart": "keyword2",
    "print-direct": "keyword2",
    "print-image": "keyword2",
    "printer-deinit": "keyword2",
    "printer-init": "keyword2",
    "put": "keyword2",
    "read": "keyword2",
    "rollback": "keyword2",
    "show": "keyword2",
    "stop": "keyword2",
    "string": "keyword2",
    "subtract": "keyword2",
    "to": "keyword2",
    "unstring": "keyword2",
    "uppercase": "keyword2",
    "use": "keyword2",
    "use-column": "keyword2",
    "use-printer-type": "keyword2",
    "use-procedure": "keyword2",
    "use-report": "keyword2",
    "where": "keyword3",
    "while": "keyword2",
    "write": "keyword2",
}

# Dictionary of keywords dictionaries for sqr mode.
keywordsDictDict = {
    "sqr_main": sqr_main_keywords_dict,
}

# Rules for sqr_main ruleset.

def sqr_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="!")

def sqr_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="'", end="'",
          no_line_break=True)

def sqr_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="[", end="]",
          no_line_break=True)

def sqr_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def sqr_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def sqr_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def sqr_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def sqr_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<>")

def sqr_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def sqr_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def sqr_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def sqr_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def sqr_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def sqr_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def sqr_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def sqr_rule15(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="$")

def sqr_rule16(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern="#")

def sqr_rule17(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="markup", pattern="&")

def sqr_rule18(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for sqr_main ruleset.
rulesDict1 = {
    "!": [sqr_rule0,],
    "#": [sqr_rule16,],
    "$": [sqr_rule15,],
    "&": [sqr_rule17,],
    "'": [sqr_rule1,],
    "*": [sqr_rule14,],
    "+": [sqr_rule12,],
    "-": [sqr_rule18,],
    "/": [sqr_rule13,],
    "0": [sqr_rule18,],
    "1": [sqr_rule18,],
    "2": [sqr_rule18,],
    "3": [sqr_rule18,],
    "4": [sqr_rule18,],
    "5": [sqr_rule18,],
    "6": [sqr_rule18,],
    "7": [sqr_rule18,],
    "8": [sqr_rule18,],
    "9": [sqr_rule18,],
    ":": [sqr_rule5,],
    "<": [sqr_rule7, sqr_rule9, sqr_rule11,],
    "=": [sqr_rule6,],
    ">": [sqr_rule8, sqr_rule10,],
    "@": [sqr_rule4, sqr_rule18,],
    "A": [sqr_rule18,],
    "B": [sqr_rule18,],
    "C": [sqr_rule18,],
    "D": [sqr_rule18,],
    "E": [sqr_rule18,],
    "F": [sqr_rule18,],
    "G": [sqr_rule18,],
    "H": [sqr_rule18,],
    "I": [sqr_rule18,],
    "J": [sqr_rule18,],
    "K": [sqr_rule18,],
    "L": [sqr_rule18,],
    "M": [sqr_rule18,],
    "N": [sqr_rule18,],
    "O": [sqr_rule18,],
    "P": [sqr_rule18,],
    "Q": [sqr_rule18,],
    "R": [sqr_rule18,],
    "S": [sqr_rule18,],
    "T": [sqr_rule18,],
    "U": [sqr_rule18,],
    "V": [sqr_rule18,],
    "W": [sqr_rule18,],
    "X": [sqr_rule18,],
    "Y": [sqr_rule18,],
    "Z": [sqr_rule18,],
    "[": [sqr_rule2,],
    "^": [sqr_rule3,],
    "a": [sqr_rule18,],
    "b": [sqr_rule18,],
    "c": [sqr_rule18,],
    "d": [sqr_rule18,],
    "e": [sqr_rule18,],
    "f": [sqr_rule18,],
    "g": [sqr_rule18,],
    "h": [sqr_rule18,],
    "i": [sqr_rule18,],
    "j": [sqr_rule18,],
    "k": [sqr_rule18,],
    "l": [sqr_rule18,],
    "m": [sqr_rule18,],
    "n": [sqr_rule18,],
    "o": [sqr_rule18,],
    "p": [sqr_rule18,],
    "q": [sqr_rule18,],
    "r": [sqr_rule18,],
    "s": [sqr_rule18,],
    "t": [sqr_rule18,],
    "u": [sqr_rule18,],
    "v": [sqr_rule18,],
    "w": [sqr_rule18,],
    "x": [sqr_rule18,],
    "y": [sqr_rule18,],
    "z": [sqr_rule18,],
}

# x.rulesDictDict for sqr mode.
rulesDictDict = {
    "sqr_main": rulesDict1,
}

# Import dict for sqr mode.
importDict = {}
