# Leo colorizer control file for fortran mode.
# This file is in the public domain.

# Properties for fortran mode.
properties = {
    "blockComment": "C",
    "indentNextLine": "\\s*((if\\s*\\(.*\\)\\s*then|else\\s*|do\\s*)*)",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for fortran_main ruleset.
fortran_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for fortran mode.
attributesDictDict = {
    "fortran_main": fortran_main_attributes_dict,
}

# Keywords dict for fortran_main ruleset.
fortran_main_keywords_dict = {
    ".false.": "keyword1",
    ".true.": "keyword1",
    "abs": "keyword1",
    "acos": "keyword1",
    "aimag": "keyword1",
    "aint": "keyword1",
    "allocatable": "keyword1",
    "allocate": "keyword1",
    "allocated": "keyword1",
    "alog": "keyword1",
    "alog10": "keyword1",
    "amax0": "keyword1",
    "amax1": "keyword1",
    "amin0": "keyword1",
    "amin1": "keyword1",
    "amod": "keyword1",
    "anint": "keyword1",
    "asin": "keyword1",
    "atan": "keyword1",
    "atan2": "keyword1",
    "backspace": "keyword1",
    "cabs": "keyword1",
    "call": "keyword1",
    "case": "keyword1",
    "ccos": "keyword1",
    "ceiling": "keyword1",
    "char": "keyword1",
    "character": "keyword1",
    "clog": "keyword1",
    "close": "keyword1",
    "cmplx": "keyword1",
    "complex": "keyword1",
    "conjg": "keyword1",
    "contains": "keyword1",
    "continue": "keyword1",
    "cos": "keyword1",
    "cosh": "keyword1",
    "csin": "keyword1",
    "csqrt": "keyword1",
    "cycle": "keyword1",
    "dabs": "keyword1",
    "dacos": "keyword1",
    "dasin": "keyword1",
    "data": "keyword1",
    "datan": "keyword1",
    "datan2": "keyword1",
    "dble": "keyword1",
    "dcmplx": "keyword1",
    "dcos": "keyword1",
    "dcosh": "keyword1",
    "ddim": "keyword1",
    "deallocate": "keyword1",
    "default": "keyword1",
    "dexp": "keyword1",
    "dfloat": "keyword1",
    "dim": "keyword1",
    "dimension": "keyword1",
    "dint": "keyword1",
    "dlog": "keyword1",
    "dlog10": "keyword1",
    "dmax1": "keyword1",
    "dmin1": "keyword1",
    "dmod": "keyword1",
    "dnint": "keyword1",
    "do": "keyword1",
    "double": "keyword1",
    "dprod": "keyword1",
    "dreal": "keyword1",
    "dsign": "keyword1",
    "dsin": "keyword1",
    "dsinh": "keyword1",
    "dsqrt": "keyword1",
    "dtan": "keyword1",
    "dtanh": "keyword1",
    "else": "keyword1",
    "elseif": "keyword1",
    "elsewhere": "keyword1",
    "end": "keyword1",
    "enddo": "keyword1",
    "endfile": "keyword1",
    "endif": "keyword1",
    "exit": "keyword1",
    "exp": "keyword1",
    "explicit": "keyword1",
    "float": "keyword1",
    "floor": "keyword1",
    "forall": "keyword1",
    "format": "keyword1",
    "function": "keyword1",
    "goto": "keyword1",
    "iabs": "keyword1",
    "ichar": "keyword1",
    "idim": "keyword1",
    "idint": "keyword1",
    "idnint": "keyword1",
    "if": "keyword1",
    "ifix": "keyword1",
    "imag": "keyword1",
    "implicit": "keyword1",
    "include": "keyword1",
    "index": "keyword1",
    "inquire": "keyword1",
    "int": "keyword1",
    "integer": "keyword1",
    "isign": "keyword1",
    "kind": "keyword1",
    "len": "keyword1",
    "lge": "keyword1",
    "lgt": "keyword1",
    "lle": "keyword1",
    "llt": "keyword1",
    "log": "keyword1",
    "log10": "keyword1",
    "logical": "keyword1",
    "max": "keyword1",
    "max0": "keyword1",
    "max1": "keyword1",
    "min": "keyword1",
    "min0": "keyword1",
    "min1": "keyword1",
    "mod": "keyword1",
    "module": "keyword1",
    "modulo": "keyword1",
    "nint": "keyword1",
    "none": "keyword1",
    "open": "keyword1",
    "parameter": "keyword1",
    "pause": "keyword1",
    "precision": "keyword1",
    "print": "keyword1",
    "program": "keyword1",
    "read": "keyword1",
    "real": "keyword1",
    "return": "keyword1",
    "rewind": "keyword1",
    "select": "keyword1",
    "sign": "keyword1",
    "sin": "keyword1",
    "sinh": "keyword1",
    "sngl": "keyword1",
    "sqrt": "keyword1",
    "stop": "keyword1",
    "subroutine": "keyword1",
    "tan": "keyword1",
    "tanh": "keyword1",
    "then": "keyword1",
    "transfer": "keyword1",
    "use": "keyword1",
    "where": "keyword1",
    "while": "keyword1",
    "write": "keyword1",
    "zext": "keyword1",
}

# Dictionary of keywords dictionaries for fortran mode.
keywordsDictDict = {
    "fortran_main": fortran_main_keywords_dict,
}

# Rules for fortran_main ruleset.

def fortran_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="c",
          at_line_start=True)

def fortran_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="C",
          at_line_start=True)

def fortran_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="!",
          at_line_start=True)

def fortran_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="*",
          at_line_start=True)

def fortran_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="!")

def fortran_rule5(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="D",
          at_line_start=True)

def fortran_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def fortran_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def fortran_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def fortran_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def fortran_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def fortran_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def fortran_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def fortran_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/=")

def fortran_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def fortran_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".lt.")

def fortran_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".gt.")

def fortran_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".eq.")

def fortran_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".ne.")

def fortran_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".le.")

def fortran_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".ge.")

def fortran_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".AND.")

def fortran_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".OR.")

def fortran_rule23(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for fortran_main ruleset.
rulesDict1 = {
    "!": [fortran_rule2, fortran_rule4,],
    "\"": [fortran_rule6,],
    "&": [fortran_rule12,],
    "'": [fortran_rule7,],
    "*": [fortran_rule3,],
    ".": [fortran_rule15, fortran_rule16, fortran_rule17, fortran_rule18, fortran_rule19, fortran_rule20, fortran_rule21, fortran_rule22, fortran_rule23,],
    "/": [fortran_rule13,],
    "0": [fortran_rule23,],
    "1": [fortran_rule23,],
    "2": [fortran_rule23,],
    "3": [fortran_rule23,],
    "4": [fortran_rule23,],
    "5": [fortran_rule23,],
    "6": [fortran_rule23,],
    "7": [fortran_rule23,],
    "8": [fortran_rule23,],
    "9": [fortran_rule23,],
    "<": [fortran_rule8, fortran_rule11,],
    "=": [fortran_rule14,],
    ">": [fortran_rule9, fortran_rule10,],
    "@": [fortran_rule23,],
    "A": [fortran_rule23,],
    "B": [fortran_rule23,],
    "C": [fortran_rule1, fortran_rule23,],
    "D": [fortran_rule5, fortran_rule23,],
    "E": [fortran_rule23,],
    "F": [fortran_rule23,],
    "G": [fortran_rule23,],
    "H": [fortran_rule23,],
    "I": [fortran_rule23,],
    "J": [fortran_rule23,],
    "K": [fortran_rule23,],
    "L": [fortran_rule23,],
    "M": [fortran_rule23,],
    "N": [fortran_rule23,],
    "O": [fortran_rule23,],
    "P": [fortran_rule23,],
    "Q": [fortran_rule23,],
    "R": [fortran_rule23,],
    "S": [fortran_rule23,],
    "T": [fortran_rule23,],
    "U": [fortran_rule23,],
    "V": [fortran_rule23,],
    "W": [fortran_rule23,],
    "X": [fortran_rule23,],
    "Y": [fortran_rule23,],
    "Z": [fortran_rule23,],
    "a": [fortran_rule23,],
    "b": [fortran_rule23,],
    "c": [fortran_rule0, fortran_rule23,],
    "d": [fortran_rule23,],
    "e": [fortran_rule23,],
    "f": [fortran_rule23,],
    "g": [fortran_rule23,],
    "h": [fortran_rule23,],
    "i": [fortran_rule23,],
    "j": [fortran_rule23,],
    "k": [fortran_rule23,],
    "l": [fortran_rule23,],
    "m": [fortran_rule23,],
    "n": [fortran_rule23,],
    "o": [fortran_rule23,],
    "p": [fortran_rule23,],
    "q": [fortran_rule23,],
    "r": [fortran_rule23,],
    "s": [fortran_rule23,],
    "t": [fortran_rule23,],
    "u": [fortran_rule23,],
    "v": [fortran_rule23,],
    "w": [fortran_rule23,],
    "x": [fortran_rule23,],
    "y": [fortran_rule23,],
    "z": [fortran_rule23,],
}

# x.rulesDictDict for fortran mode.
rulesDictDict = {
    "fortran_main": rulesDict1,
}

# Import dict for fortran mode.
importDict = {}
