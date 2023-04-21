# Leo colorizer control file for icon mode.
# This file is in the public domain.

# Properties for icon mode.
properties = {
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "#",
    "lineUpClosingBracket": "true",
    "wordBreakChars": "|.\\\\:,+-*/=?^!@%<>&",
}

# Attributes dict for icon_main ruleset.
icon_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for icon mode.
attributesDictDict = {
    "icon_main": icon_main_attributes_dict,
}

# Keywords dict for icon_main ruleset.
icon_main_keywords_dict = {
    "$define": "keyword3",
    "$else": "keyword3",
    "$endif": "keyword3",
    "$error": "keyword3",
    "$ifdef": "keyword3",
    "$ifndef": "keyword3",
    "$include": "keyword3",
    "$line": "keyword3",
    "$undef": "keyword3",
    "&": "keyword3",
    "_MACINTOSH": "keyword3",
    "_MSDOS": "keyword3",
    "_MSDOS_386": "keyword3",
    "_MS_WINDOWS": "keyword3",
    "_MS_WINDOWS_NT": "keyword3",
    "_OS2": "keyword3",
    "_PIPES": "keyword3",
    "_PRESENTATION_MGR": "keyword3",
    "_SYSTEM_FUNCTION": "keyword3",
    "_UNIX": "keyword3",
    "_VMS": "keyword3",
    "_WINDOW_FUNCTIONS": "keyword3",
    "_X_WINDOW_SYSTEM": "keyword3",
    "allocated": "keyword3",
    "ascii": "keyword3",
    "break": "keyword2",
    "by": "keyword1",
    "case": "keyword1",
    "clock": "keyword3",
    "co-expression": "keyword4",
    "collections": "keyword3",
    "create": "keyword1",
    "cset": "keyword4",
    "current": "keyword3",
    "date": "keyword3",
    "dateline": "keyword3",
    "default": "keyword1",
    "digits": "keyword3",
    "do": "keyword1",
    "dump": "keyword3",
    "e": "keyword3",
    "else": "keyword1",
    "end": "keyword2",
    "error": "keyword3",
    "errornumber": "keyword3",
    "errortext": "keyword3",
    "errorvalue": "keyword3",
    "errout": "keyword3",
    "every": "keyword1",
    "fail": "keyword3",
    "features": "keyword3",
    "file": "keyword4",
    "global": "keyword2",
    "host": "keyword3",
    "if": "keyword1",
    "initial": "keyword1",
    "input": "keyword3",
    "integer": "keyword4",
    "invocable": "keyword2",
    "lcase": "keyword3",
    "letters": "keyword3",
    "level": "keyword3",
    "line": "keyword3",
    "link": "keyword2",
    "list": "keyword4",
    "local": "keyword2",
    "main": "keyword3",
    "next": "keyword1",
    "null": "keyword4",
    "of": "keyword1",
    "output": "keyword3",
    "phi": "keyword3",
    "pi": "keyword3",
    "pos": "keyword3",
    "procedure": "keyword2",
    "progname": "keyword3",
    "random": "keyword3",
    "real": "keyword4",
    "record": "keyword2",
    "regions": "keyword3",
    "repeat": "keyword1",
    "return": "keyword2",
    "set": "keyword4",
    "source": "keyword3",
    "static": "keyword2",
    "storage": "keyword3",
    "string": "keyword4",
    "subject": "keyword3",
    "suspend": "keyword2",
    "table": "keyword4",
    "then": "keyword1",
    "time": "keyword3",
    "to": "keyword1",
    "trace": "keyword3",
    "ucase": "keyword3",
    "until": "keyword1",
    "version": "keyword3",
    "while": "keyword1",
    "window": "keyword4",
}

# Dictionary of keywords dictionaries for icon mode.
keywordsDictDict = {
    "icon_main": icon_main_keywords_dict,
}

# Rules for icon_main ruleset.

def icon_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def icon_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def icon_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="'", end="'",
          no_line_break=True)

def icon_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~===")

def icon_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="===")

def icon_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|||")

def icon_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>=")

def icon_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>")

def icon_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<<=")

def icon_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<<")

def icon_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~==")

def icon_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def icon_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="||")

def icon_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="++")

def icon_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="**")

def icon_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="--")

def icon_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<->")

def icon_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<-")

def icon_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="op:=")

def icon_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def icon_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def icon_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def icon_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def icon_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~=")

def icon_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=:")

def icon_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def icon_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-:")

def icon_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+:")

def icon_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def icon_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def icon_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def icon_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def icon_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def icon_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="not")

def icon_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def icon_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def icon_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def icon_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def icon_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def icon_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def icon_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def icon_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def icon_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def icon_rule43(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def icon_rule44(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for icon_main ruleset.
rulesDict1 = {
    "!": [icon_rule30,],
    "\"": [icon_rule1,],
    "#": [icon_rule0,],
    "$": [icon_rule44,],
    "%": [icon_rule38,],
    "&": [icon_rule32, icon_rule44,],
    "'": [icon_rule2,],
    "(": [icon_rule43,],
    "*": [icon_rule14, icon_rule34,],
    "+": [icon_rule13, icon_rule27, icon_rule40,],
    "-": [icon_rule15, icon_rule26, icon_rule39, icon_rule44,],
    "/": [icon_rule42,],
    "0": [icon_rule44,],
    "1": [icon_rule44,],
    "2": [icon_rule44,],
    "3": [icon_rule44,],
    "4": [icon_rule44,],
    "5": [icon_rule44,],
    "6": [icon_rule44,],
    "7": [icon_rule44,],
    "8": [icon_rule44,],
    "9": [icon_rule44,],
    ":": [icon_rule24, icon_rule25, icon_rule29,],
    "<": [icon_rule8, icon_rule9, icon_rule16, icon_rule17, icon_rule19, icon_rule20,],
    "=": [icon_rule4, icon_rule11, icon_rule41,],
    ">": [icon_rule6, icon_rule7, icon_rule21, icon_rule22,],
    "?": [icon_rule35,],
    "@": [icon_rule36, icon_rule44,],
    "A": [icon_rule44,],
    "B": [icon_rule44,],
    "C": [icon_rule44,],
    "D": [icon_rule44,],
    "E": [icon_rule44,],
    "F": [icon_rule44,],
    "G": [icon_rule44,],
    "H": [icon_rule44,],
    "I": [icon_rule44,],
    "J": [icon_rule44,],
    "K": [icon_rule44,],
    "L": [icon_rule44,],
    "M": [icon_rule44,],
    "N": [icon_rule44,],
    "O": [icon_rule44,],
    "P": [icon_rule44,],
    "Q": [icon_rule44,],
    "R": [icon_rule44,],
    "S": [icon_rule44,],
    "T": [icon_rule44,],
    "U": [icon_rule44,],
    "V": [icon_rule44,],
    "W": [icon_rule44,],
    "X": [icon_rule44,],
    "Y": [icon_rule44,],
    "Z": [icon_rule44,],
    "^": [icon_rule37,],
    "_": [icon_rule44,],
    "a": [icon_rule44,],
    "b": [icon_rule44,],
    "c": [icon_rule44,],
    "d": [icon_rule44,],
    "e": [icon_rule44,],
    "f": [icon_rule44,],
    "g": [icon_rule44,],
    "h": [icon_rule44,],
    "i": [icon_rule44,],
    "j": [icon_rule44,],
    "k": [icon_rule44,],
    "l": [icon_rule44,],
    "m": [icon_rule44,],
    "n": [icon_rule33, icon_rule44,],
    "o": [icon_rule18, icon_rule44,],
    "p": [icon_rule44,],
    "q": [icon_rule44,],
    "r": [icon_rule44,],
    "s": [icon_rule44,],
    "t": [icon_rule44,],
    "u": [icon_rule44,],
    "v": [icon_rule44,],
    "w": [icon_rule44,],
    "x": [icon_rule44,],
    "y": [icon_rule44,],
    "z": [icon_rule44,],
    "|": [icon_rule5, icon_rule12, icon_rule31,],
    "~": [icon_rule3, icon_rule10, icon_rule23, icon_rule28,],
}

# x.rulesDictDict for icon mode.
rulesDictDict = {
    "icon_main": rulesDict1,
}

# Import dict for icon mode.
importDict = {}
