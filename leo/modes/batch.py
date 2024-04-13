#@+leo-ver=5-thin
#@+node:ekr.20221129095254.1: * @file ../modes/batch.py
#@@language python

# Leo colorizer control file for batch mode.
# This file is in the public domain.

# Properties for batch mode.
properties = {
    "lineComment": "rem",
}

# Attributes dict for batch_main ruleset.
batch_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for batch mode.
attributesDictDict = {
    "batch_main": batch_main_attributes_dict,
}

# Keywords dict for batch_main ruleset.
batch_main_keywords_dict = {
    "append": "function",
    "attrib": "function",
    "aux": "keyword2",
    "call": "keyword1",
    "cd": "keyword1",
    "chdir": "keyword1",
    "chkdsk": "function",
    "choice": "function",
    "cls": "keyword1",
    "copy": "keyword1",
    "debug": "function",
    "defined": "keyword2",
    "defrag": "function",
    "del": "keyword1",
    "deltree": "function",
    "diskcomp": "function",
    "diskcopy": "function",
    "do": "keyword2",
    "doskey": "function",
    "drvspace": "function",
    "echo": "keyword1",
    "echo.": "keyword1",
    "else": "keyword2",
    "emm386": "function",
    "endlocal": "keyword1",
    "errorlevel": "keyword2",
    "exist": "keyword2",
    "exit": "keyword1",
    "expand": "function",
    "fastopen": "function",
    "fc": "function",
    "fdisk": "function",
    "find": "function",
    "for": "keyword1",
    "format": "function",
    "goto": "keyword3",
    "graphics": "function",
    "if": "keyword1",
    "in": "keyword2",
    "keyb": "function",
    "label": "function",
    "loadfix": "function",
    "md": "keyword1",
    "mem": "function",
    "mkdir": "keyword1",
    "mode": "function",
    "more": "function",
    "move": "function",
    "mscdex": "function",
    "nlsfunc": "function",
    "not": "keyword1",
    "nul": "keyword2",
    "pause": "keyword1",
    "power": "function",
    "print": "function",
    "prn": "keyword2",
    "rd": "function",
    "ren": "keyword1",
    "replace": "function",
    "restore": "function",
    "set": "keyword1",
    "setlocal": "keyword1",
    "setver": "function",
    "share": "function",
    "shift": "keyword1",
    "sort": "function",
    "subst": "function",
    "sys": "function",
    "tree": "function",
    "undelete": "function",
    "unformat": "function",
    "vsafe": "function",
    "xcopy": "function",
}

# Dictionary of keywords dictionaries for batch mode.
keywordsDictDict = {
    "batch_main": batch_main_keywords_dict,
}

# Rules for batch_main ruleset.

#@+others
#@+node:ekr.20221129095311.1: ** batch_rule0
def batch_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="@")
#@+node:ekr.20221129095311.2: ** batch_rule1
def batch_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")
#@+node:ekr.20221129095311.3: ** batch_rule2
def batch_rule2(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

#@+node:ekr.20221129095311.4: ** batch_rule3
def batch_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")


#@+node:ekr.20221129095311.5: ** batch_rule4
def batch_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")


#@+node:ekr.20221129095311.6: ** batch_rule5
def batch_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

#@+node:ekr.20221129095311.7: ** batch_rule6
def batch_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")


#@+node:ekr.20221129095311.8: ** batch_rule7
def batch_rule7(colorer, s, i):
    # Labels.
    return colorer.match_eol_span(s, i, kind="label", seq=":",
        at_line_start=True)
#@+node:ekr.20221129095311.9: ** batch_rule8
def batch_rule8(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="REM",
        at_line_start=True, at_whitespace_end=True, at_word_start=True)

def batch_rule8a(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="rem",
        at_line_start=True, at_whitespace_end=True, at_word_start=True)



#@+node:ekr.20221129095311.10: ** batch_rule9
def batch_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        no_line_break=True)

#@+node:ekr.20221129095311.11: ** batch_rule10
def batch_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="%0")


#@+node:ekr.20221129095311.12: ** batch_rule11
def batch_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="%1")


#@+node:ekr.20221129095311.13: ** batch_rule12
def batch_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="%2")


#@+node:ekr.20221129095311.14: ** batch_rule13
def batch_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="%3")


#@+node:ekr.20221129095311.15: ** batch_rule14
def batch_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="%4")


#@+node:ekr.20221129095311.16: ** batch_rule15
def batch_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="%5")


#@+node:ekr.20221129095311.17: ** batch_rule16
def batch_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="%6")


#@+node:ekr.20221129095311.18: ** batch_rule17
def batch_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="%7")


#@+node:ekr.20221129095311.19: ** batch_rule18
def batch_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="%8")


#@+node:ekr.20221129095311.20: ** batch_rule19
def batch_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="%9")


#@+node:ekr.20221129095311.21: ** batch_rule20
def batch_rule20(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="%[", end="]")


#@+node:ekr.20221129095311.22: ** batch_rule21
def batch_rule21(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="%", end="%",
        no_line_break=True)
#@+node:ekr.20221129095311.23: ** batch_rule22
def batch_rule22(colorer, s, i):
    return colorer.match_keywords(s, i)

#@-others
# Rules dict for batch_main ruleset.
rulesDict1 = {
    "!": [batch_rule4],
    "\"": [batch_rule9],
    "%": [
        batch_rule10, batch_rule11, batch_rule12, batch_rule13, batch_rule14,
        batch_rule15, batch_rule16, batch_rule17, batch_rule18, batch_rule19,
        batch_rule20, batch_rule21
    ],
    "&": [batch_rule3],
    "+": [batch_rule1],
    ".": [batch_rule22],
    "0": [batch_rule22],
    "1": [batch_rule22],
    "2": [batch_rule22],
    "3": [batch_rule22],
    "4": [batch_rule22],
    "5": [batch_rule22],
    "6": [batch_rule22],
    "7": [batch_rule22],
    "8": [batch_rule22],
    "9": [batch_rule22],
    ":": [batch_rule7],
    "<": [batch_rule6],
    ">": [batch_rule5],
    "@": [batch_rule0, batch_rule22],
    "A": [batch_rule22],
    "B": [batch_rule22],
    "C": [batch_rule22],
    "D": [batch_rule22],
    "E": [batch_rule22],
    "F": [batch_rule22],
    "G": [batch_rule22],
    "H": [batch_rule22],
    "I": [batch_rule22],
    "J": [batch_rule22],
    "K": [batch_rule22],
    "L": [batch_rule22],
    "M": [batch_rule22],
    "N": [batch_rule22],
    "O": [batch_rule22],
    "P": [batch_rule22],
    "Q": [batch_rule22],
    "R": [batch_rule8, batch_rule22],
    "S": [batch_rule22],
    "T": [batch_rule22],
    "U": [batch_rule22],
    "V": [batch_rule22],
    "W": [batch_rule22],
    "X": [batch_rule22],
    "Y": [batch_rule22],
    "Z": [batch_rule22],
    "a": [batch_rule22],
    "b": [batch_rule22],
    "c": [batch_rule22],
    "d": [batch_rule22],
    "e": [batch_rule22],
    "f": [batch_rule22],
    "g": [batch_rule22],
    "h": [batch_rule22],
    "i": [batch_rule22],
    "j": [batch_rule22],
    "k": [batch_rule22],
    "l": [batch_rule22],
    "m": [batch_rule22],
    "n": [batch_rule22],
    "o": [batch_rule22],
    "p": [batch_rule22],
    "q": [batch_rule22],
    "r": [batch_rule8a, batch_rule22],
    "s": [batch_rule22],
    "t": [batch_rule22],
    "u": [batch_rule22],
    "v": [batch_rule22],
    "w": [batch_rule22],
    "x": [batch_rule22],
    "y": [batch_rule22],
    "z": [batch_rule22],
    "|": [batch_rule2],
}

# x.rulesDictDict for batch mode.
rulesDictDict = {
    "batch_main": rulesDict1,
}

# Import dict for batch mode.
importDict = {}
#@@language python
#@@tabwidth -4
#@-leo
