# Leo colorizer control file for rview mode.
# This file is in the public domain.

# Properties for rview mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
}

# Attributes dict for rview_main ruleset.
rview_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for rview_rviewstmt ruleset.
rview_rviewstmt_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for rview mode.
attributesDictDict = {
    "rview_main": rview_main_attributes_dict,
    "rview_rviewstmt": rview_rviewstmt_attributes_dict,
}

# Keywords dict for rview_main ruleset.
rview_main_keywords_dict = {
    "BIGINT": "keyword3",
    "BINARY": "keyword3",
    "BIT": "keyword3",
    "CHAR": "keyword3",
    "DATE": "keyword3",
    "DECIMAL": "keyword3",
    "DOUBLE": "keyword3",
    "FLOAT": "keyword3",
    "INTEGER": "keyword3",
    "LONGVARBINARY": "keyword3",
    "LONGVARCHAR": "keyword3",
    "NUMERIC": "keyword3",
    "REAL": "keyword3",
    "SMALLINT": "keyword3",
    "TIME": "keyword3",
    "TIMESTAMP": "keyword3",
    "TINYINT": "keyword3",
    "VARBINARY": "keyword3",
    "VARCHAR": "keyword3",
    "allow": "keyword1",
    "boolean": "keyword3",
    "byte": "keyword3",
    "case": "keyword1",
    "char": "keyword3",
    "class": "keyword1",
    "constraints": "keyword1",
    "delete": "keyword1",
    "distinct": "keyword1",
    "double": "keyword3",
    "float": "keyword3",
    "function": "keyword1",
    "insert": "keyword1",
    "int": "keyword3",
    "join": "keyword1",
    "jointype": "keyword1",
    "leftouter": "keyword1",
    "long": "keyword3",
    "orderby": "keyword1",
    "query": "keyword1",
    "relationalview": "keyword1",
    "return": "keyword1",
    "rightouter": "keyword1",
    "rowmap": "keyword1",
    "select": "keyword1",
    "short": "keyword3",
    "sql": "keyword1",
    "subview": "keyword1",
    "switch": "keyword1",
    "table": "keyword1",
    "unique": "keyword1",
    "update": "keyword1",
    "useCallableStatement": "keyword1",
    "where": "keyword1",
}

# Keywords dict for rview_rviewstmt ruleset.
rview_rviewstmt_keywords_dict = {
    "and": "keyword1",
    "between": "keyword1",
    "bigint": "keyword3",
    "binary": "keyword3",
    "bit": "keyword3",
    "call": "keyword1",
    "char": "keyword3",
    "date": "keyword3",
    "decimal": "keyword3",
    "desc": "keyword1",
    "double": "keyword3",
    "float": "keyword3",
    "from": "keyword1",
    "in": "keyword1",
    "integer": "keyword3",
    "longvarbinary": "keyword3",
    "longvarchar": "keyword3",
    "not": "keyword1",
    "numeric": "keyword3",
    "real": "keyword3",
    "select": "keyword1",
    "set": "keyword1",
    "smallint": "keyword3",
    "time": "keyword3",
    "timestamp": "keyword3",
    "tinyint": "keyword3",
    "update": "keyword1",
    "varbinary": "keyword3",
    "varchar": "keyword3",
    "where": "keyword1",
}

# Dictionary of keywords dictionaries for rview mode.
keywordsDictDict = {
    "rview_main": rview_main_keywords_dict,
    "rview_rviewstmt": rview_rviewstmt_keywords_dict,
}

# Rules for rview_main ruleset.

def rview_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment1", seq="/**/")

def rview_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="/**", end="*/",
          delegate="rview::javadoc")

def rview_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def rview_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="rview::rviewstmt",
          no_line_break=True)

def rview_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def rview_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def rview_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def rview_rule7(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def rview_rule8(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def rview_rule9(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for rview_main ruleset.
rulesDict1 = {
    "\"": [rview_rule3,],
    "(": [rview_rule7,],
    "/": [rview_rule0, rview_rule1, rview_rule2, rview_rule8,],
    "0": [rview_rule9,],
    "1": [rview_rule9,],
    "2": [rview_rule9,],
    "3": [rview_rule9,],
    "4": [rview_rule9,],
    "5": [rview_rule9,],
    "6": [rview_rule9,],
    "7": [rview_rule9,],
    "8": [rview_rule9,],
    "9": [rview_rule9,],
    "=": [rview_rule6,],
    "@": [rview_rule9,],
    "A": [rview_rule9,],
    "B": [rview_rule9,],
    "C": [rview_rule9,],
    "D": [rview_rule9,],
    "E": [rview_rule9,],
    "F": [rview_rule9,],
    "G": [rview_rule9,],
    "H": [rview_rule9,],
    "I": [rview_rule9,],
    "J": [rview_rule9,],
    "K": [rview_rule9,],
    "L": [rview_rule9,],
    "M": [rview_rule9,],
    "N": [rview_rule9,],
    "O": [rview_rule9,],
    "P": [rview_rule9,],
    "Q": [rview_rule9,],
    "R": [rview_rule9,],
    "S": [rview_rule9,],
    "T": [rview_rule9,],
    "U": [rview_rule9,],
    "V": [rview_rule9,],
    "W": [rview_rule9,],
    "X": [rview_rule9,],
    "Y": [rview_rule9,],
    "Z": [rview_rule9,],
    "a": [rview_rule9,],
    "b": [rview_rule9,],
    "c": [rview_rule9,],
    "d": [rview_rule9,],
    "e": [rview_rule9,],
    "f": [rview_rule9,],
    "g": [rview_rule9,],
    "h": [rview_rule9,],
    "i": [rview_rule9,],
    "j": [rview_rule9,],
    "k": [rview_rule9,],
    "l": [rview_rule9,],
    "m": [rview_rule9,],
    "n": [rview_rule9,],
    "o": [rview_rule9,],
    "p": [rview_rule9,],
    "q": [rview_rule9,],
    "r": [rview_rule9,],
    "s": [rview_rule9,],
    "t": [rview_rule9,],
    "u": [rview_rule9,],
    "v": [rview_rule9,],
    "w": [rview_rule9,],
    "x": [rview_rule9,],
    "y": [rview_rule9,],
    "z": [rview_rule9,],
    "{": [rview_rule5,],
    "}": [rview_rule4,],
}

# Rules for rview_rviewstmt ruleset.

def rview_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def rview_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def rview_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def rview_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def rview_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def rview_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def rview_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def rview_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def rview_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def rview_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def rview_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def rview_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def rview_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="::")

def rview_rule23(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="label", pattern=":")

def rview_rule24(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def rview_rule25(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for rview_rviewstmt ruleset.
rulesDict2 = {
    "'": [rview_rule10,],
    "(": [rview_rule24,],
    "*": [rview_rule14,],
    "+": [rview_rule11,],
    "-": [rview_rule12,],
    "/": [rview_rule13,],
    "0": [rview_rule25,],
    "1": [rview_rule25,],
    "2": [rview_rule25,],
    "3": [rview_rule25,],
    "4": [rview_rule25,],
    "5": [rview_rule25,],
    "6": [rview_rule25,],
    "7": [rview_rule25,],
    "8": [rview_rule25,],
    "9": [rview_rule25,],
    ":": [rview_rule22, rview_rule23,],
    "<": [rview_rule17, rview_rule19,],
    "=": [rview_rule15,],
    ">": [rview_rule16, rview_rule18,],
    "@": [rview_rule25,],
    "A": [rview_rule25,],
    "B": [rview_rule25,],
    "C": [rview_rule25,],
    "D": [rview_rule25,],
    "E": [rview_rule25,],
    "F": [rview_rule25,],
    "G": [rview_rule25,],
    "H": [rview_rule25,],
    "I": [rview_rule25,],
    "J": [rview_rule25,],
    "K": [rview_rule25,],
    "L": [rview_rule25,],
    "M": [rview_rule25,],
    "N": [rview_rule25,],
    "O": [rview_rule25,],
    "P": [rview_rule25,],
    "Q": [rview_rule25,],
    "R": [rview_rule25,],
    "S": [rview_rule25,],
    "T": [rview_rule25,],
    "U": [rview_rule25,],
    "V": [rview_rule25,],
    "W": [rview_rule25,],
    "X": [rview_rule25,],
    "Y": [rview_rule25,],
    "Z": [rview_rule25,],
    "a": [rview_rule25,],
    "b": [rview_rule25,],
    "c": [rview_rule25,],
    "d": [rview_rule25,],
    "e": [rview_rule25,],
    "f": [rview_rule25,],
    "g": [rview_rule25,],
    "h": [rview_rule25,],
    "i": [rview_rule25,],
    "j": [rview_rule25,],
    "k": [rview_rule25,],
    "l": [rview_rule25,],
    "m": [rview_rule25,],
    "n": [rview_rule25,],
    "o": [rview_rule25,],
    "p": [rview_rule25,],
    "q": [rview_rule25,],
    "r": [rview_rule25,],
    "s": [rview_rule25,],
    "t": [rview_rule25,],
    "u": [rview_rule25,],
    "v": [rview_rule25,],
    "w": [rview_rule25,],
    "x": [rview_rule25,],
    "y": [rview_rule25,],
    "z": [rview_rule25,],
    "{": [rview_rule21,],
    "}": [rview_rule20,],
}

# x.rulesDictDict for rview mode.
rulesDictDict = {
    "rview_main": rulesDict1,
    "rview_rviewstmt": rulesDict2,
}

# Import dict for rview mode.
importDict = {}
