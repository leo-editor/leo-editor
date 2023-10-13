#@+leo-ver=5-thin
#@+node:ekr.20231012163843.1: * @file ../modes/scheme.py
# Leo colorizer control file for scheme mode.
# This file is in the public domain.

# Properties for scheme mode.
properties = {
    "commentEnd": "|#",
    "commentStart": "#|",
    "indentCloseBrackets": ")",
    "indentOpenBrackets": "(",
    "lineComment": ";",
    "lineUpClosingBracket": "false",
    "noWordSep": "_-+?:*/!",
}

# Attributes dict for scheme_main ruleset.
scheme_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "_-+?:*/!",
}

# Dictionary of attributes dictionaries for scheme mode.
attributesDictDict = {
    "scheme_main": scheme_main_attributes_dict,
}

# Keywords dict for scheme_main ruleset.
scheme_main_keywords_dict = {
    "#f": "literal2",
    "#t": "literal2",
    "<": "keyword3",
    "=?": "keyword3",
    ">": "keyword3",
    "?": "keyword3",
    "abs": "keyword2",
    "acos": "keyword2",
    "and": "keyword1",
    "angle": "keyword2",
    "append": "keyword2",
    "apply": "keyword2",
    "asin": "keyword2",
    "assoc": "keyword2",
    "assq": "keyword2",
    "assv": "keyword2",
    "atan": "keyword2",
    "begin": "keyword1",
    "boolean?": "keyword3",
    "caaar": "keyword2",
    "caadr": "keyword2",
    "caar": "keyword2",
    "cadar": "keyword2",
    "caddr": "keyword2",
    "cadr": "keyword2",
    "call-with-current-continuation": "keyword2",
    "call-with-input-file": "keyword2",
    "call-with-output-file": "keyword2",
    "call-with-values": "keyword2",
    "call/cc": "keyword2",
    "car": "keyword2",
    "case": "keyword1",
    "catch": "keyword2",
    "cdaar": "keyword2",
    "cdadr": "keyword2",
    "cdar": "keyword2",
    "cddar": "keyword2",
    "cdddr": "keyword2",
    "cddr": "keyword2",
    "cdr": "keyword2",
    "ceiling": "keyword2",
    "char": "keyword3",
    "char-": "keyword2",
    "char-alphabetic?": "keyword3",
    "char-ci": "keyword3",
    "char-ci=?": "keyword3",
    "char-downcase": "keyword2",
    "char-lower-case?": "keyword3",
    "char-numeric?": "keyword3",
    "char-ready?": "keyword3",
    "char-upcase": "keyword2",
    "char-upper-case?": "keyword3",
    "char-whitespace?": "keyword3",
    "char=?": "keyword3",
    "char?": "keyword3",
    "close-input-port": "keyword2",
    "close-output-port": "keyword2",
    "complex?": "keyword3",
    "cond": "keyword1",
    "cond-expand": "keyword1",
    "cons": "keyword2",
    "cos": "keyword2",
    "current-input-port": "keyword2",
    "current-output-port": "keyword2",
    "define": "keyword1",
    "define-macro": "keyword1",
    "delay": "keyword1",
    "delete-file": "keyword2",
    "display": "keyword2",
    "do": "keyword1",
    "dynamic-wind": "keyword2",
    "else": "keyword1",
    "eof-object?": "keyword3",
    "eq?": "keyword3",
    "equal?": "keyword3",
    "eqv?": "keyword3",
    "eval": "keyword2",
    "even?": "keyword3",
    "exact-": "keyword2",
    "exact?": "keyword3",
    "exit": "keyword2",
    "exp": "keyword2",
    "expt": "keyword2",
    "file-exists?": "keyword3",
    "file-or-directory-modify-seconds": "keyword2",
    "floor": "keyword2",
    "fluid-let": "keyword1",
    "for-each": "keyword2",
    "force": "keyword2",
    "gcd": "keyword2",
    "gensym": "keyword2",
    "get-output-string": "keyword2",
    "getenv": "keyword2",
    "if": "keyword1",
    "imag-part": "keyword2",
    "inexact": "keyword2",
    "inexact?": "keyword3",
    "input-port?": "keyword3",
    "integer": "keyword2",
    "integer-": "keyword2",
    "integer?": "keyword3",
    "lambda": "keyword1",
    "lcm": "keyword2",
    "length": "keyword2",
    "let": "keyword1",
    "let*": "keyword1",
    "letrec": "keyword1",
    "list": "keyword2",
    "list-": "keyword2",
    "list-ref": "keyword2",
    "list-tail": "keyword2",
    "list?": "keyword3",
    "load": "keyword2",
    "log": "keyword2",
    "magnitude": "keyword2",
    "make-polar": "keyword2",
    "make-rectangular": "keyword2",
    "make-string": "keyword2",
    "make-vector": "keyword2",
    "map": "keyword2",
    "max": "keyword2",
    "member": "keyword2",
    "memq": "keyword2",
    "memv": "keyword2",
    "min": "keyword2",
    "modulo": "keyword2",
    "negative?": "keyword3",
    "newline": "keyword2",
    "nil": "keyword2",
    "not": "keyword2",
    "null?": "keyword3",
    "number": "keyword2",
    "number-": "keyword2",
    "number?": "keyword3",
    "odd?": "keyword3",
    "open-input-file": "keyword2",
    "open-input-string": "keyword2",
    "open-output-file": "keyword2",
    "open-output-string": "keyword2",
    "or": "keyword1",
    "output-port?": "keyword3",
    "pair?": "keyword3",
    "peek-char": "keyword2",
    "port?": "keyword3",
    "positive?": "keyword3",
    "procedure?": "keyword3",
    "quasiquote": "keyword1",
    "quote": "keyword1",
    "quotient": "keyword2",
    "rational?": "keyword3",
    "read": "keyword2",
    "read-char": "keyword2",
    "read-line": "keyword2",
    "real-part": "keyword2",
    "real?": "keyword3",
    "remainder": "keyword2",
    "reverse": "keyword2",
    "reverse!": "keyword2",
    "round": "keyword2",
    "set!": "keyword1",
    "set-car!": "keyword2",
    "set-cdr!": "keyword2",
    "sin": "keyword2",
    "sqrt": "keyword2",
    "string": "keyword3",
    "string-": "keyword2",
    "string-append": "keyword2",
    "string-ci": "keyword3",
    "string-ci=?": "keyword3",
    "string-copy": "keyword2",
    "string-fill!": "keyword2",
    "string-length": "keyword2",
    "string-ref": "keyword2",
    "string-set!": "keyword2",
    "string=?": "keyword3",
    "string?": "keyword3",
    "substring": "keyword2",
    "symbol": "keyword2",
    "symbol-": "keyword2",
    "symbol?": "keyword3",
    "system": "keyword2",
    "tan": "keyword2",
    "truncate": "keyword2",
    "values": "keyword2",
    "vector": "keyword2",
    "vector-": "keyword2",
    "vector-fill!": "keyword2",
    "vector-length": "keyword2",
    "vector-ref": "keyword2",
    "vector-set!": "keyword2",
    "vector?": "keyword3",
    "with-input-from-file": "keyword2",
    "with-output-to-file": "keyword2",
    "write": "keyword2",
    "write-char": "keyword2",
    "zero?": "keyword3",
}

# Dictionary of keywords dictionaries for scheme mode.
keywordsDictDict = {
    "scheme_main": scheme_main_keywords_dict,
}

# Rules for scheme_main ruleset.

def scheme_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="#|", end="|#")

def scheme_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="'(")

def scheme_rule2(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="'")

def scheme_rule3(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="#\\")

def scheme_rule4(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="#b")

def scheme_rule5(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="#d")

def scheme_rule6(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="#o")

def scheme_rule7(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="#x")

def scheme_rule8(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";")

def scheme_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def scheme_rule10(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for scheme_main ruleset.
rulesDict1 = {
    "!": [scheme_rule10,],
    "\"": [scheme_rule9,],
    "#": [scheme_rule0, scheme_rule3, scheme_rule4, scheme_rule5, scheme_rule6, scheme_rule7, scheme_rule10,],
    "'": [scheme_rule1, scheme_rule2,],
    "*": [scheme_rule10,],
    "-": [scheme_rule10,],
    "/": [scheme_rule10,],
    "0": [scheme_rule10,],
    "1": [scheme_rule10,],
    "2": [scheme_rule10,],
    "3": [scheme_rule10,],
    "4": [scheme_rule10,],
    "5": [scheme_rule10,],
    "6": [scheme_rule10,],
    "7": [scheme_rule10,],
    "8": [scheme_rule10,],
    "9": [scheme_rule10,],
    ";": [scheme_rule8,],
    "<": [scheme_rule10,],
    "=": [scheme_rule10,],
    ">": [scheme_rule10,],
    "?": [scheme_rule10,],
    "@": [scheme_rule10,],
    "A": [scheme_rule10,],
    "B": [scheme_rule10,],
    "C": [scheme_rule10,],
    "D": [scheme_rule10,],
    "E": [scheme_rule10,],
    "F": [scheme_rule10,],
    "G": [scheme_rule10,],
    "H": [scheme_rule10,],
    "I": [scheme_rule10,],
    "J": [scheme_rule10,],
    "K": [scheme_rule10,],
    "L": [scheme_rule10,],
    "M": [scheme_rule10,],
    "N": [scheme_rule10,],
    "O": [scheme_rule10,],
    "P": [scheme_rule10,],
    "Q": [scheme_rule10,],
    "R": [scheme_rule10,],
    "S": [scheme_rule10,],
    "T": [scheme_rule10,],
    "U": [scheme_rule10,],
    "V": [scheme_rule10,],
    "W": [scheme_rule10,],
    "X": [scheme_rule10,],
    "Y": [scheme_rule10,],
    "Z": [scheme_rule10,],
    "a": [scheme_rule10,],
    "b": [scheme_rule10,],
    "c": [scheme_rule10,],
    "d": [scheme_rule10,],
    "e": [scheme_rule10,],
    "f": [scheme_rule10,],
    "g": [scheme_rule10,],
    "h": [scheme_rule10,],
    "i": [scheme_rule10,],
    "j": [scheme_rule10,],
    "k": [scheme_rule10,],
    "l": [scheme_rule10,],
    "m": [scheme_rule10,],
    "n": [scheme_rule10,],
    "o": [scheme_rule10,],
    "p": [scheme_rule10,],
    "q": [scheme_rule10,],
    "r": [scheme_rule10,],
    "s": [scheme_rule10,],
    "t": [scheme_rule10,],
    "u": [scheme_rule10,],
    "v": [scheme_rule10,],
    "w": [scheme_rule10,],
    "x": [scheme_rule10,],
    "y": [scheme_rule10,],
    "z": [scheme_rule10,],
}

# x.rulesDictDict for scheme mode.
rulesDictDict = {
    "scheme_main": rulesDict1,
}

# Import dict for scheme mode.
importDict = {}
#@-leo
