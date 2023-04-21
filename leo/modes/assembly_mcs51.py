# Leo colorizer control file for assembly_mcs51 mode.
# This file is in the public domain.

# Properties for assembly_mcs51 mode.
properties = {
    "lineComment": ";",
}

# Attributes dict for assembly_mcs51_main ruleset.
assembly_mcs51_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for assembly_mcs51 mode.
attributesDictDict = {
    "assembly_mcs51_main": assembly_mcs51_main_attributes_dict,
}

# Keywords dict for assembly_mcs51_main ruleset.
assembly_mcs51_main_keywords_dict = {
    "$CASE": "keyword2",
    "$ELSE": "keyword2",
    "$ELSEIF": "keyword2",
    "$ENDIF": "keyword2",
    "$IF": "keyword2",
    "$INCLUDE": "keyword2",
    "$MOD167": "keyword2",
    "$SEGMENTED": "keyword2",
    "A": "keyword3",
    "AB": "keyword3",
    "ACALL": "keyword1",
    "ADD": "keyword1",
    "ADDC": "keyword1",
    "ADDM": "keyword1",
    "AJMP": "keyword1",
    "AND": "keyword1",
    "ANL": "keyword1",
    "AT": "keyword1",
    "BIT": "keyword2",
    "BITADDRESSABLE": "keyword1",
    "BSEG": "keyword1",
    "C": "keyword3",
    "CALL": "keyword1",
    "CJNE": "keyword1",
    "CLR": "keyword1",
    "CODE": "keyword2",
    "CPL": "keyword1",
    "CSEG": "keyword1",
    "DA": "keyword1",
    "DATA": "keyword2",
    "DB": "keyword1",
    "DBIT": "keyword1",
    "DEC": "keyword1",
    "DEFINE": "keyword1",
    "DIV": "keyword1",
    "DJNZ": "keyword1",
    "DPTN": "keyword1",
    "DPTR": "keyword1",
    "DPTR16": "keyword1",
    "DPTR8": "keyword1",
    "DPTX": "keyword1",
    "DR0": "keyword1",
    "DR4": "keyword1",
    "DS": "keyword1",
    "DSEG": "keyword1",
    "DW": "keyword1",
    "DWR": "keyword1",
    "ELSE": "keyword1",
    "ELSEIF": "keyword1",
    "END": "keyword1",
    "ENDIF": "keyword1",
    "ENDM": "keyword1",
    "EQ": "keyword1",
    "EQS": "keyword1",
    "EQU": "keyword1",
    "EXITM": "keyword1",
    "EXTRN": "keyword1",
    "FI": "keyword1",
    "GE": "keyword1",
    "GT": "keyword1",
    "HIGH": "keyword1",
    "IDATA": "keyword2",
    "IF": "keyword1",
    "INBLOCK": "keyword1",
    "INC": "keyword1",
    "INPAGE": "keyword1",
    "IRP": "keyword1",
    "IRPC": "keyword1",
    "ISEG": "keyword1",
    "JB": "keyword1",
    "JBC": "keyword1",
    "JC": "keyword1",
    "JMP": "keyword1",
    "JMPI": "keyword1",
    "JNB": "keyword1",
    "JNC": "keyword1",
    "JNZ": "keyword1",
    "JZ": "keyword1",
    "LCALL": "keyword1",
    "LE": "keyword1",
    "LEN": "keyword1",
    "LJMP": "keyword1",
    "LOCAL": "keyword1",
    "LOW": "keyword1",
    "LT": "keyword1",
    "MACRO": "keyword1",
    "MOD": "keyword1",
    "MOV": "keyword1",
    "MOVB": "keyword1",
    "MOVC": "keyword1",
    "MOVX": "keyword1",
    "MUL": "keyword1",
    "NAME": "keyword1",
    "NE": "keyword1",
    "NOP": "keyword1",
    "NOT": "keyword1",
    "NUL": "keyword1",
    "NUMBER": "keyword1",
    "OR": "keyword1",
    "ORG": "keyword1",
    "ORL": "keyword1",
    "OVERLAYABLE": "keyword1",
    "PAGE": "keyword1",
    "PC": "keyword1",
    "POP": "keyword1",
    "POPA": "keyword1",
    "PUBLIC": "keyword1",
    "PUSH": "keyword1",
    "PUSHA": "keyword1",
    "R0": "keyword3",
    "R1": "keyword3",
    "R2": "keyword3",
    "R3": "keyword3",
    "R4": "keyword3",
    "R5": "keyword3",
    "R6": "keyword3",
    "R7": "keyword3",
    "REPT": "keyword1",
    "RET": "keyword1",
    "RETI": "keyword1",
    "RJC": "keyword1",
    "RJNC": "keyword1",
    "RJNZ": "keyword1",
    "RJZ": "keyword1",
    "RL": "keyword1",
    "RLC": "keyword1",
    "RR": "keyword1",
    "RRC": "keyword1",
    "RSEG": "keyword1",
    "SBIT": "keyword1",
    "SEGMENT": "keyword1",
    "SET": "keyword1",
    "SETB": "keyword1",
    "SFR": "keyword1",
    "SFR16": "keyword1",
    "SHL": "keyword1",
    "SHR": "keyword1",
    "SJMP": "keyword1",
    "SLEEP": "keyword1",
    "SP": "keyword3",
    "STACKLEN": "keyword1",
    "SUB": "keyword1",
    "SUBB": "keyword1",
    "SUBM": "keyword1",
    "SUBSTR": "keyword1",
    "SWAP": "keyword1",
    "SYNC": "keyword1",
    "THEN": "keyword1",
    "UNIT": "keyword1",
    "USING": "keyword1",
    "WR0": "keyword1",
    "WR2": "keyword1",
    "WR4": "keyword1",
    "WR6": "keyword1",
    "XCH": "keyword1",
    "XCHD": "keyword1",
    "XDATA": "keyword2",
    "XOR": "keyword1",
    "XRL": "keyword1",
    "XSEG": "keyword1",
    "__ERROR__": "keyword1",
}

# Dictionary of keywords dictionaries for assembly_mcs51 mode.
keywordsDictDict = {
    "assembly_mcs51_main": assembly_mcs51_main_keywords_dict,
}

# Rules for assembly_mcs51_main ruleset.

def assembly_mcs51_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";")

def assembly_mcs51_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def assembly_mcs51_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def assembly_mcs51_rule3(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="label", pattern="%%",
          at_line_start=True,
          exclude_match=True)

def assembly_mcs51_rule4(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$",
          at_line_start=True)

def assembly_mcs51_rule5(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_line_start=True,
          exclude_match=True)

def assembly_mcs51_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=",")

def assembly_mcs51_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=":")

def assembly_mcs51_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="(")

def assembly_mcs51_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=")")

def assembly_mcs51_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="]")

def assembly_mcs51_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="[")

def assembly_mcs51_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="$")

def assembly_mcs51_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def assembly_mcs51_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def assembly_mcs51_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def assembly_mcs51_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def assembly_mcs51_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def assembly_mcs51_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def assembly_mcs51_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def assembly_mcs51_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def assembly_mcs51_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def assembly_mcs51_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def assembly_mcs51_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def assembly_mcs51_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def assembly_mcs51_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def assembly_mcs51_rule26(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for assembly_mcs51_main ruleset.
rulesDict1 = {
    "!": [assembly_mcs51_rule22,],
    "\"": [assembly_mcs51_rule2,],
    "$": [assembly_mcs51_rule4, assembly_mcs51_rule12, assembly_mcs51_rule26,],
    "%": [assembly_mcs51_rule3, assembly_mcs51_rule17,],
    "&": [assembly_mcs51_rule20,],
    "'": [assembly_mcs51_rule1,],
    "(": [assembly_mcs51_rule8,],
    ")": [assembly_mcs51_rule9,],
    "*": [assembly_mcs51_rule16,],
    "+": [assembly_mcs51_rule13,],
    ",": [assembly_mcs51_rule6,],
    "-": [assembly_mcs51_rule14,],
    "/": [assembly_mcs51_rule15,],
    "0": [assembly_mcs51_rule26,],
    "1": [assembly_mcs51_rule26,],
    "2": [assembly_mcs51_rule26,],
    "3": [assembly_mcs51_rule26,],
    "4": [assembly_mcs51_rule26,],
    "5": [assembly_mcs51_rule26,],
    "6": [assembly_mcs51_rule26,],
    "7": [assembly_mcs51_rule26,],
    "8": [assembly_mcs51_rule26,],
    "9": [assembly_mcs51_rule26,],
    ":": [assembly_mcs51_rule5, assembly_mcs51_rule7,],
    ";": [assembly_mcs51_rule0,],
    "<": [assembly_mcs51_rule24,],
    "=": [assembly_mcs51_rule23,],
    ">": [assembly_mcs51_rule25,],
    "@": [assembly_mcs51_rule26,],
    "A": [assembly_mcs51_rule26,],
    "B": [assembly_mcs51_rule26,],
    "C": [assembly_mcs51_rule26,],
    "D": [assembly_mcs51_rule26,],
    "E": [assembly_mcs51_rule26,],
    "F": [assembly_mcs51_rule26,],
    "G": [assembly_mcs51_rule26,],
    "H": [assembly_mcs51_rule26,],
    "I": [assembly_mcs51_rule26,],
    "J": [assembly_mcs51_rule26,],
    "K": [assembly_mcs51_rule26,],
    "L": [assembly_mcs51_rule26,],
    "M": [assembly_mcs51_rule26,],
    "N": [assembly_mcs51_rule26,],
    "O": [assembly_mcs51_rule26,],
    "P": [assembly_mcs51_rule26,],
    "Q": [assembly_mcs51_rule26,],
    "R": [assembly_mcs51_rule26,],
    "S": [assembly_mcs51_rule26,],
    "T": [assembly_mcs51_rule26,],
    "U": [assembly_mcs51_rule26,],
    "V": [assembly_mcs51_rule26,],
    "W": [assembly_mcs51_rule26,],
    "X": [assembly_mcs51_rule26,],
    "Y": [assembly_mcs51_rule26,],
    "Z": [assembly_mcs51_rule26,],
    "[": [assembly_mcs51_rule11,],
    "]": [assembly_mcs51_rule10,],
    "^": [assembly_mcs51_rule19,],
    "_": [assembly_mcs51_rule26,],
    "a": [assembly_mcs51_rule26,],
    "b": [assembly_mcs51_rule26,],
    "c": [assembly_mcs51_rule26,],
    "d": [assembly_mcs51_rule26,],
    "e": [assembly_mcs51_rule26,],
    "f": [assembly_mcs51_rule26,],
    "g": [assembly_mcs51_rule26,],
    "h": [assembly_mcs51_rule26,],
    "i": [assembly_mcs51_rule26,],
    "j": [assembly_mcs51_rule26,],
    "k": [assembly_mcs51_rule26,],
    "l": [assembly_mcs51_rule26,],
    "m": [assembly_mcs51_rule26,],
    "n": [assembly_mcs51_rule26,],
    "o": [assembly_mcs51_rule26,],
    "p": [assembly_mcs51_rule26,],
    "q": [assembly_mcs51_rule26,],
    "r": [assembly_mcs51_rule26,],
    "s": [assembly_mcs51_rule26,],
    "t": [assembly_mcs51_rule26,],
    "u": [assembly_mcs51_rule26,],
    "v": [assembly_mcs51_rule26,],
    "w": [assembly_mcs51_rule26,],
    "x": [assembly_mcs51_rule26,],
    "y": [assembly_mcs51_rule26,],
    "z": [assembly_mcs51_rule26,],
    "|": [assembly_mcs51_rule18,],
    "~": [assembly_mcs51_rule21,],
}

# x.rulesDictDict for assembly_mcs51 mode.
rulesDictDict = {
    "assembly_mcs51_main": rulesDict1,
}

# Import dict for assembly_mcs51 mode.
importDict = {}
