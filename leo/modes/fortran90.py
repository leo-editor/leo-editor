# Leo colorizer control file for fortran90 mode.
# This file is in the public domain.

# Properties for fortran90 mode.
properties = {
    "blockComment": "!",
    "indentNextLine": "\\s*((if\\s*\\(.*\\)\\s*then|else\\s*|do\\s*)*)",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for fortran90_main ruleset.
fortran90_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for fortran90 mode.
attributesDictDict = {
    "fortran90_main": fortran90_main_attributes_dict,
}

# Keywords dict for fortran90_main ruleset.
fortran90_main_keywords_dict = {
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

# Dictionary of keywords dictionaries for fortran90 mode.
keywordsDictDict = {
    "fortran90_main": fortran90_main_keywords_dict,
}

# Rules for fortran90_main ruleset.

def fortran90_rule0(colorer, s, i):
    return colorer.match_terminate(s, i, kind="", at_char=132)

def fortran90_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="!")

def fortran90_rule2(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def fortran90_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def fortran90_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def fortran90_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def fortran90_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def fortran90_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/=")

def fortran90_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def fortran90_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".lt.")

def fortran90_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".gt.")

def fortran90_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".eq.")

def fortran90_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".ne.")

def fortran90_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".le.")

def fortran90_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".ge.")

def fortran90_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".AND.")

def fortran90_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".OR.")

def fortran90_rule17(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for fortran90_main ruleset.
rulesDict1 = {
    "!": [fortran90_rule1,],
    "&": [fortran90_rule6,],
    ".": [fortran90_rule9, fortran90_rule10, fortran90_rule11, fortran90_rule12, fortran90_rule13, fortran90_rule14, fortran90_rule15, fortran90_rule16, fortran90_rule17,],
    "/": [fortran90_rule7,],
    "0": [fortran90_rule17,],
    "1": [fortran90_rule17,],
    "2": [fortran90_rule17,],
    "3": [fortran90_rule17,],
    "4": [fortran90_rule17,],
    "5": [fortran90_rule17,],
    "6": [fortran90_rule17,],
    "7": [fortran90_rule17,],
    "8": [fortran90_rule17,],
    "9": [fortran90_rule17,],
    "<": [fortran90_rule2, fortran90_rule5,],
    "=": [fortran90_rule8,],
    ">": [fortran90_rule3, fortran90_rule4,],
    "@": [fortran90_rule17,],
    "A": [fortran90_rule17,],
    "B": [fortran90_rule17,],
    "C": [fortran90_rule17,],
    "D": [fortran90_rule17,],
    "E": [fortran90_rule17,],
    "F": [fortran90_rule17,],
    "G": [fortran90_rule17,],
    "H": [fortran90_rule17,],
    "I": [fortran90_rule17,],
    "J": [fortran90_rule17,],
    "K": [fortran90_rule17,],
    "L": [fortran90_rule17,],
    "M": [fortran90_rule17,],
    "N": [fortran90_rule17,],
    "O": [fortran90_rule17,],
    "P": [fortran90_rule17,],
    "Q": [fortran90_rule17,],
    "R": [fortran90_rule17,],
    "S": [fortran90_rule17,],
    "T": [fortran90_rule17,],
    "U": [fortran90_rule17,],
    "V": [fortran90_rule17,],
    "W": [fortran90_rule17,],
    "X": [fortran90_rule17,],
    "Y": [fortran90_rule17,],
    "Z": [fortran90_rule17,],
    "a": [fortran90_rule17,],
    "b": [fortran90_rule17,],
    "c": [fortran90_rule17,],
    "d": [fortran90_rule17,],
    "e": [fortran90_rule17,],
    "f": [fortran90_rule17,],
    "g": [fortran90_rule17,],
    "h": [fortran90_rule17,],
    "i": [fortran90_rule17,],
    "j": [fortran90_rule17,],
    "k": [fortran90_rule17,],
    "l": [fortran90_rule17,],
    "m": [fortran90_rule17,],
    "n": [fortran90_rule17,],
    "o": [fortran90_rule17,],
    "p": [fortran90_rule17,],
    "q": [fortran90_rule17,],
    "r": [fortran90_rule17,],
    "s": [fortran90_rule17,],
    "t": [fortran90_rule17,],
    "u": [fortran90_rule17,],
    "v": [fortran90_rule17,],
    "w": [fortran90_rule17,],
    "x": [fortran90_rule17,],
    "y": [fortran90_rule17,],
    "z": [fortran90_rule17,],
}

# x.rulesDictDict for fortran90 mode.
rulesDictDict = {
    "fortran90_main": rulesDict1,
}

# Import dict for fortran90 mode.
importDict = {}
