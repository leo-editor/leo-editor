# Leo colorizer control file for interlis mode.
# This file is in the public domain.

# Properties for interlis mode.
properties = {
    "blockComment": "!!",
    "commentEnd": "*/",
    "commentStart": "/*",
}

# Attributes dict for interlis_main ruleset.
interlis_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for interlis mode.
attributesDictDict = {
    "interlis_main": interlis_main_attributes_dict,
}

# Keywords dict for interlis_main ruleset.
interlis_main_keywords_dict = {
    "ABSTRACT": "keyword1",
    "ACCORDING": "keyword1",
    "AGGREGATES": "keyword1",
    "AGGREGATION": "keyword1",
    "ALL": "keyword1",
    "AND": "keyword1",
    "ANY": "keyword1",
    "ARCS": "keyword1",
    "AREA": "keyword1",
    "ASSOCIATION": "keyword1",
    "ATTRIBUTE": "keyword1",
    "ATTRIBUTES": "keyword1",
    "BAG": "keyword1",
    "BASE": "keyword1",
    "BASED": "keyword1",
    "BASKET": "keyword1",
    "BLANK": "keyword1",
    "BOOLEAN": "keyword1",
    "BY": "keyword1",
    "CIRCULAR": "keyword1",
    "CLASS": "keyword1",
    "CLOCKWISE": "keyword1",
    "CODE": "keyword1",
    "CONSTRAINT": "keyword1",
    "CONSTRAINTS": "keyword1",
    "CONTINUE": "keyword1",
    "CONTINUOUS": "keyword1",
    "CONTOUR": "keyword1",
    "CONTRACT": "keyword1",
    "COORD": "keyword1",
    "COORD2": "keyword1",
    "COORD3": "keyword1",
    "COUNTERCLOCKWISE": "keyword1",
    "DATE": "keyword1",
    "DEFAULT": "keyword1",
    "DEFINED": "keyword1",
    "DEGREES": "keyword1",
    "DEPENDS": "keyword1",
    "DERIVATIVES": "keyword1",
    "DERIVED": "keyword1",
    "DIM1": "keyword1",
    "DIM2": "keyword1",
    "DIRECTED": "keyword1",
    "DOMAIN": "keyword1",
    "END": "keyword1",
    "EQUAL": "keyword1",
    "EXISTENCE": "keyword1",
    "EXTENDS": "keyword1",
    "FIRST": "keyword1",
    "FIX": "keyword1",
    "FONT": "keyword1",
    "FORM": "keyword1",
    "FORMAT": "keyword1",
    "FREE": "keyword1",
    "FROM": "keyword1",
    "FUNCTION": "keyword1",
    "GRADS": "keyword1",
    "GRAPHIC": "keyword1",
    "HALIGNMENT": "keyword1",
    "I16": "keyword1",
    "I32": "keyword1",
    "IDENT": "keyword1",
    "IMPORTS": "keyword1",
    "IN": "keyword1",
    "INSPECTION": "keyword1",
    "INTERLIS": "keyword1",
    "ISSUED": "keyword1",
    "JOIN": "keyword1",
    "LAST": "keyword1",
    "LINE": "keyword1",
    "LINEATTR": "keyword1",
    "LINESIZE": "keyword1",
    "LIST": "keyword1",
    "LNBASE": "keyword1",
    "MANDATORY": "keyword1",
    "METAOBJECT": "keyword1",
    "MODEL": "keyword1",
    "NAME": "keyword1",
    "NO": "keyword1",
    "NOT": "keyword1",
    "NULL": "keyword1",
    "NUMERIC": "keyword1",
    "OBJECT": "keyword1",
    "OF": "keyword1",
    "ON": "keyword1",
    "OPTIONAL": "keyword1",
    "OR": "keyword1",
    "ORDERED": "keyword1",
    "OVERLAPS": "keyword1",
    "PARAMETER": "keyword1",
    "PARENT": "keyword1",
    "PATTERN": "keyword1",
    "PERIPHERY": "keyword1",
    "PI": "keyword1",
    "POLYLINE": "keyword1",
    "PREFIX": "keyword1",
    "PROJECTION": "keyword1",
    "RADIANS": "keyword1",
    "REFERENCE": "keyword1",
    "REFSYSTEM": "keyword1",
    "REQUIRED": "keyword1",
    "RESTRICTED": "keyword1",
    "ROTATION": "keyword1",
    "SELECTION": "keyword1",
    "SIGN": "keyword1",
    "STRAIGHTS": "keyword1",
    "STRUCTURE": "keyword1",
    "SURFACE": "keyword1",
    "SYMBOLOGY": "keyword1",
    "TABLE": "keyword1",
    "TEXT": "keyword1",
    "THATAREA": "keyword1",
    "THIS": "keyword1",
    "THISAREA": "keyword1",
    "TID": "keyword1",
    "TIDSIZE": "keyword1",
    "TO": "keyword1",
    "TOPIC": "keyword1",
    "TRANSFER": "keyword1",
    "TRANSLATION": "keyword1",
    "TYPE": "keyword1",
    "UNDEFINED": "keyword1",
    "UNION": "keyword1",
    "UNIQUE": "keyword1",
    "UNIT": "keyword1",
    "URI": "keyword1",
    "USES": "keyword1",
    "VALIGNMENT": "keyword1",
    "VERTEX": "keyword1",
    "VERTEXINFO": "keyword1",
    "VIEW": "keyword1",
    "WHEN": "keyword1",
    "WHERE": "keyword1",
    "WITH": "keyword1",
    "WITHOUT": "keyword1",
}

# Dictionary of keywords dictionaries for interlis mode.
keywordsDictDict = {
    "interlis_main": interlis_main_keywords_dict,
}

# Rules for interlis_main ruleset.

def interlis_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def interlis_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="!!")

def interlis_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def interlis_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="//", end="//")

def interlis_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="->")

def interlis_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<-")

def interlis_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="..")

def interlis_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def interlis_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def interlis_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def interlis_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def interlis_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def interlis_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def interlis_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def interlis_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def interlis_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def interlis_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def interlis_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def interlis_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!=")

def interlis_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="#")

def interlis_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def interlis_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def interlis_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def interlis_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def interlis_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def interlis_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="--")

def interlis_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-<#>")

def interlis_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-<>")

def interlis_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="->")

def interlis_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def interlis_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="..")

def interlis_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def interlis_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def interlis_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def interlis_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def interlis_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def interlis_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def interlis_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<>")

def interlis_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def interlis_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def interlis_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def interlis_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def interlis_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def interlis_rule43(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\\")

def interlis_rule44(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def interlis_rule45(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def interlis_rule46(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def interlis_rule47(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def interlis_rule48(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for interlis_main ruleset.
rulesDict1 = {
    "!": [interlis_rule1, interlis_rule18,],
    "\"": [interlis_rule2,],
    "#": [interlis_rule19,],
    "%": [interlis_rule20,],
    "(": [interlis_rule15, interlis_rule21,],
    ")": [interlis_rule16, interlis_rule22,],
    "*": [interlis_rule12, interlis_rule23,],
    ",": [interlis_rule8, interlis_rule24,],
    "-": [interlis_rule4, interlis_rule25, interlis_rule26, interlis_rule27, interlis_rule28,],
    ".": [interlis_rule6, interlis_rule7, interlis_rule29, interlis_rule30,],
    "/": [interlis_rule0, interlis_rule3, interlis_rule31,],
    "0": [interlis_rule48,],
    "1": [interlis_rule48,],
    "2": [interlis_rule48,],
    "3": [interlis_rule48,],
    "4": [interlis_rule48,],
    "5": [interlis_rule48,],
    "6": [interlis_rule48,],
    "7": [interlis_rule48,],
    "8": [interlis_rule48,],
    "9": [interlis_rule48,],
    ":": [interlis_rule11, interlis_rule32, interlis_rule33,],
    ";": [interlis_rule10, interlis_rule34,],
    "<": [interlis_rule5, interlis_rule35, interlis_rule36, interlis_rule37,],
    "=": [interlis_rule9, interlis_rule38, interlis_rule39,],
    ">": [interlis_rule17, interlis_rule40, interlis_rule41,],
    "@": [interlis_rule48,],
    "A": [interlis_rule48,],
    "B": [interlis_rule48,],
    "C": [interlis_rule48,],
    "D": [interlis_rule48,],
    "E": [interlis_rule48,],
    "F": [interlis_rule48,],
    "G": [interlis_rule48,],
    "H": [interlis_rule48,],
    "I": [interlis_rule48,],
    "J": [interlis_rule48,],
    "K": [interlis_rule48,],
    "L": [interlis_rule48,],
    "M": [interlis_rule48,],
    "N": [interlis_rule48,],
    "O": [interlis_rule48,],
    "P": [interlis_rule48,],
    "Q": [interlis_rule48,],
    "R": [interlis_rule48,],
    "S": [interlis_rule48,],
    "T": [interlis_rule48,],
    "U": [interlis_rule48,],
    "V": [interlis_rule48,],
    "W": [interlis_rule48,],
    "X": [interlis_rule48,],
    "Y": [interlis_rule48,],
    "Z": [interlis_rule48,],
    "[": [interlis_rule13, interlis_rule42,],
    "\\": [interlis_rule43,],
    "]": [interlis_rule14, interlis_rule44,],
    "a": [interlis_rule48,],
    "b": [interlis_rule48,],
    "c": [interlis_rule48,],
    "d": [interlis_rule48,],
    "e": [interlis_rule48,],
    "f": [interlis_rule48,],
    "g": [interlis_rule48,],
    "h": [interlis_rule48,],
    "i": [interlis_rule48,],
    "j": [interlis_rule48,],
    "k": [interlis_rule48,],
    "l": [interlis_rule48,],
    "m": [interlis_rule48,],
    "n": [interlis_rule48,],
    "o": [interlis_rule48,],
    "p": [interlis_rule48,],
    "q": [interlis_rule48,],
    "r": [interlis_rule48,],
    "s": [interlis_rule48,],
    "t": [interlis_rule48,],
    "u": [interlis_rule48,],
    "v": [interlis_rule48,],
    "w": [interlis_rule48,],
    "x": [interlis_rule48,],
    "y": [interlis_rule48,],
    "z": [interlis_rule48,],
    "{": [interlis_rule45,],
    "}": [interlis_rule46,],
    "~": [interlis_rule47,],
}

# x.rulesDictDict for interlis mode.
rulesDictDict = {
    "interlis_main": rulesDict1,
}

# Import dict for interlis mode.
importDict = {}
