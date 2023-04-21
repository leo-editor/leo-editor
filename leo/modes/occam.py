# Leo colorizer control file for occam mode.
# This file is in the public domain.

# Properties for occam mode.
properties = {
    "blockComment": "",
    "commentEnd": "",
    "commentStart": "--",
    "noWordSep": ".",
}

# Attributes dict for occam_main ruleset.
occam_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for occam mode.
attributesDictDict = {
    "occam_main": occam_main_attributes_dict,
}

# Keywords dict for occam_main ruleset.
occam_main_keywords_dict = {
    "ABS": "keyword3",
    "AFTER": "keyword2",
    "ALOG": "keyword3",
    "ALOG10": "keyword3",
    "ALT": "keyword1",
    "AND": "keyword2",
    "ANY": "keyword2",
    "ARGUMENT.REDUCE": "keyword3",
    "ASHIFTLEFT": "keyword3",
    "ASHIFTRIGHT": "keyword3",
    "ASIN": "keyword3",
    "ASM": "keyword1",
    "ASSERT": "keyword3",
    "AT": "keyword2",
    "ATAN": "keyword3",
    "ATAN2": "keyword3",
    "BITAND": "keyword2",
    "BITNOT": "keyword2",
    "BITOR": "keyword2",
    "BOOL": "keyword2",
    "BOOLTOSTRING": "keyword3",
    "BUCKET": "keyword2",
    "BYTE": "keyword2",
    "BYTESIN": "keyword2",
    "CASE": "keyword1",
    "CHAN": "keyword2",
    "CLAIM": "keyword2",
    "COPYSIGN": "keyword3",
    "COS": "keyword3",
    "COSH": "keyword3",
    "DABS": "keyword3",
    "DALOG": "keyword3",
    "DALOG10": "keyword3",
    "DARGUMENT.REDUCE": "keyword3",
    "DASIN": "keyword3",
    "DATA": "keyword2",
    "DATAN": "keyword3",
    "DATAN2": "keyword3",
    "DCOPYSIGN": "keyword3",
    "DCOS": "keyword3",
    "DCOSH": "keyword3",
    "DDIVBY2": "keyword3",
    "DEXP": "keyword3",
    "DFLOATING.UNPACK": "keyword3",
    "DFPINT": "keyword3",
    "DIEEECOMPARE": "keyword3",
    "DISNAN": "keyword3",
    "DIVBY2": "keyword3",
    "DLOGB": "keyword3",
    "DMINUSX": "keyword3",
    "DMULBY2": "keyword3",
    "DNEXTAFTER": "keyword3",
    "DNOTFINITE": "keyword3",
    "DORDERED": "keyword3",
    "DPOWER": "keyword3",
    "DRAN": "keyword3",
    "DSCALEB": "keyword3",
    "DSIN": "keyword3",
    "DSINH": "keyword3",
    "DSQRT": "keyword3",
    "DTAN": "keyword3",
    "DTANH": "keyword3",
    "ELSE": "keyword2",
    "ENROLL": "keyword2",
    "EVENT": "keyword2",
    "EXP": "keyword3",
    "FALL": "keyword2",
    "FALSE": "literal2",
    "FLOATING.UNPACK": "keyword3",
    "FLUSH": "keyword2",
    "FOR": "keyword2",
    "FPINT": "keyword3",
    "FROM": "keyword2",
    "FUNCTION": "keyword1",
    "GRANT": "keyword2",
    "HEX16TOSTRING": "keyword3",
    "HEX32TOSTRING": "keyword3",
    "HEX64TOSTRING": "keyword3",
    "HEXTOSTRING": "keyword3",
    "IEEE32OP": "keyword3",
    "IEEE32REM": "keyword3",
    "IEEE64OP": "keyword3",
    "IEEE64REM": "keyword3",
    "IEEECOMPARE": "keyword3",
    "IF": "keyword1",
    "INITIAL": "keyword2",
    "INLINE": "keyword1",
    "INT": "keyword2",
    "INT16": "keyword2",
    "INT16TOSTRING": "keyword3",
    "INT32": "keyword2",
    "INT32TOSTRING": "keyword3",
    "INT64": "keyword2",
    "INT64TOSTRING": "keyword3",
    "INTTOSTRING": "keyword3",
    "IS": "keyword2",
    "ISNAN": "keyword3",
    "LOGB": "keyword3",
    "LONGADD": "keyword3",
    "LONGDIFF": "keyword3",
    "LONGDIV": "keyword3",
    "LONGPROD": "keyword3",
    "LONGSUB": "keyword3",
    "LONGSUM": "keyword3",
    "MINUS": "keyword2",
    "MINUSX": "keyword3",
    "MOSTNEG": "keyword2",
    "MOSTPOS": "keyword2",
    "MULBY2": "keyword3",
    "NEXTAFTER": "keyword3",
    "NORMALISE": "keyword3",
    "NOT": "keyword2",
    "NOTFINITE": "keyword3",
    "OF": "keyword2",
    "OFFSETOF": "keyword2",
    "OR": "keyword2",
    "ORDERED": "keyword3",
    "PACKED": "keyword2",
    "PAR": "keyword1",
    "PLACE": "keyword2",
    "PLACED": "keyword1",
    "PLUS": "keyword2",
    "PORT": "keyword2",
    "POWER": "keyword3",
    "PRI": "keyword1",
    "PROC": "keyword1",
    "PROTOCOL": "keyword2",
    "RAN": "keyword3",
    "REAL32": "keyword2",
    "REAL32EQ": "keyword3",
    "REAL32GT": "keyword3",
    "REAL32OP": "keyword3",
    "REAL32REM": "keyword3",
    "REAL32TOSTRING": "keyword3",
    "REAL64": "keyword2",
    "REAL64EQ": "keyword3",
    "REAL64GT": "keyword3",
    "REAL64OP": "keyword3",
    "REAL64REM": "keyword3",
    "REAL64TOSTRING": "keyword3",
    "RECORD": "keyword2",
    "REM": "keyword2",
    "RESCHEDULE": "keyword3",
    "RESHAPES": "keyword2",
    "RESOURCE": "keyword2",
    "RESULT": "keyword1",
    "RETYPES": "keyword2",
    "ROTATELEFT": "keyword3",
    "ROTATERIGHT": "keyword3",
    "ROUND": "keyword2",
    "SCALEB": "keyword3",
    "SEMAPHORE": "keyword2",
    "SEQ": "keyword1",
    "SHARED": "keyword2",
    "SHIFTLEFT": "keyword3",
    "SHIFTRIGHT": "keyword3",
    "SIN": "keyword3",
    "SINH": "keyword3",
    "SIZE": "keyword2",
    "SKIP": "keyword2",
    "SQRT": "keyword3",
    "STOP": "keyword2",
    "STRINGTOBOOL": "keyword3",
    "STRINGTOHEX": "keyword3",
    "STRINGTOHEX16": "keyword3",
    "STRINGTOHEX32": "keyword3",
    "STRINGTOHEX64": "keyword3",
    "STRINGTOINT": "keyword3",
    "STRINGTOINT16": "keyword3",
    "STRINGTOINT32": "keyword3",
    "STRINGTOINT64": "keyword3",
    "STRINGTOREAL32": "keyword3",
    "STRINGTOREAL64": "keyword3",
    "SYNC": "keyword2",
    "TAN": "keyword3",
    "TANH": "keyword3",
    "TIMER": "keyword2",
    "TIMES": "keyword2",
    "TRUE": "literal2",
    "TRUNC": "keyword2",
    "TYPE": "keyword2",
    "VAL": "keyword2",
    "VALOF": "keyword1",
    "WHILE": "keyword1",
}

# Dictionary of keywords dictionaries for occam mode.
keywordsDictDict = {
    "occam_main": occam_main_keywords_dict,
}

# Rules for occam_main ruleset.

def occam_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def occam_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="#")

def occam_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def occam_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def occam_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def occam_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def occam_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>")

def occam_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<<")

def occam_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<>")

def occam_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="><")

def occam_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def occam_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def occam_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def occam_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def occam_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def occam_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def occam_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def occam_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def occam_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def occam_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def occam_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def occam_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/\\")

def occam_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\/")

def occam_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def occam_rule24(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for occam_main ruleset.
rulesDict1 = {
    "!": [occam_rule20,],
    "\"": [occam_rule3,],
    "#": [occam_rule1,],
    "'": [occam_rule2,],
    "*": [occam_rule18,],
    "+": [occam_rule14,],
    "-": [occam_rule0, occam_rule15,],
    ".": [occam_rule24,],
    "/": [occam_rule16, occam_rule21,],
    "0": [occam_rule24,],
    "1": [occam_rule24,],
    "2": [occam_rule24,],
    "3": [occam_rule24,],
    "4": [occam_rule24,],
    "5": [occam_rule24,],
    "6": [occam_rule24,],
    "7": [occam_rule24,],
    "8": [occam_rule24,],
    "9": [occam_rule24,],
    ":": [occam_rule4,],
    "<": [occam_rule7, occam_rule8, occam_rule11, occam_rule13,],
    "=": [occam_rule5,],
    ">": [occam_rule6, occam_rule9, occam_rule10, occam_rule12,],
    "?": [occam_rule19,],
    "@": [occam_rule24,],
    "A": [occam_rule24,],
    "B": [occam_rule24,],
    "C": [occam_rule24,],
    "D": [occam_rule24,],
    "E": [occam_rule24,],
    "F": [occam_rule24,],
    "G": [occam_rule24,],
    "H": [occam_rule24,],
    "I": [occam_rule24,],
    "J": [occam_rule24,],
    "K": [occam_rule24,],
    "L": [occam_rule24,],
    "M": [occam_rule24,],
    "N": [occam_rule24,],
    "O": [occam_rule24,],
    "P": [occam_rule24,],
    "Q": [occam_rule24,],
    "R": [occam_rule24,],
    "S": [occam_rule24,],
    "T": [occam_rule24,],
    "U": [occam_rule24,],
    "V": [occam_rule24,],
    "W": [occam_rule24,],
    "X": [occam_rule24,],
    "Y": [occam_rule24,],
    "Z": [occam_rule24,],
    "\\": [occam_rule17, occam_rule22,],
    "a": [occam_rule24,],
    "b": [occam_rule24,],
    "c": [occam_rule24,],
    "d": [occam_rule24,],
    "e": [occam_rule24,],
    "f": [occam_rule24,],
    "g": [occam_rule24,],
    "h": [occam_rule24,],
    "i": [occam_rule24,],
    "j": [occam_rule24,],
    "k": [occam_rule24,],
    "l": [occam_rule24,],
    "m": [occam_rule24,],
    "n": [occam_rule24,],
    "o": [occam_rule24,],
    "p": [occam_rule24,],
    "q": [occam_rule24,],
    "r": [occam_rule24,],
    "s": [occam_rule24,],
    "t": [occam_rule24,],
    "u": [occam_rule24,],
    "v": [occam_rule24,],
    "w": [occam_rule24,],
    "x": [occam_rule24,],
    "y": [occam_rule24,],
    "z": [occam_rule24,],
    "~": [occam_rule23,],
}

# x.rulesDictDict for occam mode.
rulesDictDict = {
    "occam_main": rulesDict1,
}

# Import dict for occam mode.
importDict = {}
