# Leo colorizer control file for pop11 mode.
# This file is in the public domain.

# Properties for pop11 mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "lineComment": ";;;",
}

# Attributes dict for pop11_main ruleset.
pop11_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for pop11_list ruleset.
pop11_list_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for pop11_string ruleset.
pop11_string_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for pop11_comment ruleset.
pop11_comment_attributes_dict = {
    "default": "COMMENT1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": ".",
}

# Dictionary of attributes dictionaries for pop11 mode.
attributesDictDict = {
    "pop11_comment": pop11_comment_attributes_dict,
    "pop11_list": pop11_list_attributes_dict,
    "pop11_main": pop11_main_attributes_dict,
    "pop11_string": pop11_string_attributes_dict,
}

# Keywords dict for pop11_main ruleset.
pop11_main_keywords_dict = {
    "add": "literal2",
    "alladd": "literal2",
    "and": "keyword2",
    "biginteger": "keyword1",
    "boolean": "keyword1",
    "by": "keyword3",
    "case": "keyword3",
    "class": "keyword1",
    "complex": "keyword1",
    "cons_with": "keyword2",
    "consclosure": "literal2",
    "consstring": "keyword2",
    "copydata": "literal2",
    "copylist": "literal2",
    "copytree": "literal2",
    "database": "literal2",
    "datalength": "literal2",
    "dataword": "literal2",
    "ddecimal": "keyword1",
    "decimal": "keyword1",
    "define": "keyword1",
    "delete": "literal2",
    "device": "keyword1",
    "dlocal": "keyword1",
    "do": "keyword3",
    "else": "keyword3",
    "elseif": "keyword3",
    "enddefine": "keyword1",
    "endfor": "keyword3",
    "endforevery": "keyword3",
    "endif": "keyword3",
    "endinstance": "keyword1",
    "endrepeat": "keyword3",
    "endswitchon": "keyword3",
    "endwhile": "keyword3",
    "false": "literal2",
    "for": "keyword3",
    "forevery": "keyword3",
    "from": "keyword3",
    "goto": "keyword2",
    "hd": "literal2",
    "ident": "keyword1",
    "if": "keyword3",
    "in": "keyword3",
    "instance": "keyword1",
    "integer": "keyword1",
    "interrupt": "literal2",
    "intvec": "keyword1",
    "isboolean": "literal2",
    "isinteger": "literal2",
    "islist": "literal2",
    "isnumber": "literal2",
    "it": "literal2",
    "key": "keyword1",
    "last": "literal2",
    "length": "literal2",
    "listlength": "literal2",
    "lvars": "keyword1",
    "matches": "keyword2",
    "max": "literal2",
    "member": "literal2",
    "method": "keyword1",
    "mishap": "literal2",
    "nil": "keyword1",
    "nl": "literal2",
    "not": "literal2",
    "oneof": "literal2",
    "or": "keyword2",
    "pair": "keyword1",
    "partapply": "literal2",
    "pr": "literal2",
    "present": "literal2",
    "procedure": "keyword1",
    "process": "keyword1",
    "prologterm": "keyword1",
    "prologvar": "keyword1",
    "quitif": "literal2",
    "quitloop": "keyword2",
    "random": "literal2",
    "ratio": "keyword1",
    "readline": "literal2",
    "ref": "keyword1",
    "remove": "literal2",
    "repeat": "keyword3",
    "return": "keyword3",
    "rev": "literal2",
    "section": "keyword1",
    "shuffle": "literal2",
    "slot": "keyword1",
    "sort": "literal2",
    "step": "keyword3",
    "string": "keyword1",
    "subword": "literal2",
    "switchon": "keyword3",
    "syntax": "keyword1",
    "syssort": "literal2",
    "termin": "keyword1",
    "then": "keyword3",
    "till": "keyword3",
    "times": "keyword3",
    "tl": "literal2",
    "to": "keyword3",
    "trace": "keyword2",
    "true": "literal2",
    "undef": "literal2",
    "uses": "keyword2",
    "valof": "literal2",
    "vars": "keyword1",
    "vector": "keyword1",
    "while": "keyword3",
    "word": "keyword1",
}

# Keywords dict for pop11_list ruleset.
pop11_list_keywords_dict = {}

# Keywords dict for pop11_string ruleset.
pop11_string_keywords_dict = {}

# Keywords dict for pop11_comment ruleset.
pop11_comment_keywords_dict = {}

# Dictionary of keywords dictionaries for pop11 mode.
keywordsDictDict = {
    "pop11_comment": pop11_comment_keywords_dict,
    "pop11_list": pop11_list_keywords_dict,
    "pop11_main": pop11_main_keywords_dict,
    "pop11_string": pop11_string_keywords_dict,
}

# Rules for pop11_main ruleset.

def pop11_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/",
          delegate="pop11::comment")

def pop11_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";;;")

def pop11_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="pop11::string",
          no_line_break=True)

def pop11_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="pop11::string",
          no_line_break=True)

def pop11_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="`", end="`",
          delegate="pop11::string",
          no_line_break=True)

def pop11_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="[", end="]",
          delegate="pop11::list")

def pop11_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="{", end="}",
          delegate="pop11::list")

def pop11_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="![", end="]",
          delegate="pop11::list")

def pop11_rule8(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def pop11_rule9(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_line_start=True)

def pop11_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="#_<")

def pop11_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=">_#")

def pop11_rule12(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="label", pattern="#_",
          at_line_start=True)

def pop11_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=")")

def pop11_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="(")

def pop11_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=".")

def pop11_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=",")

def pop11_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=";")

def pop11_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="^")

def pop11_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="@")

def pop11_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=":")

def pop11_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="|")

def pop11_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def pop11_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def pop11_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def pop11_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<>")

def pop11_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def pop11_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def pop11_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def pop11_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def pop11_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def pop11_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def pop11_rule32(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for pop11_main ruleset.
rulesDict1 = {
    "!": [pop11_rule7,],
    "\"": [pop11_rule3,],
    "#": [pop11_rule10, pop11_rule12,],
    "'": [pop11_rule2,],
    "(": [pop11_rule8, pop11_rule14,],
    ")": [pop11_rule13,],
    "*": [pop11_rule31,],
    "+": [pop11_rule28,],
    ",": [pop11_rule16,],
    "-": [pop11_rule30,],
    ".": [pop11_rule15,],
    "/": [pop11_rule0, pop11_rule29,],
    "0": [pop11_rule32,],
    "1": [pop11_rule32,],
    "2": [pop11_rule32,],
    "3": [pop11_rule32,],
    "4": [pop11_rule32,],
    "5": [pop11_rule32,],
    "6": [pop11_rule32,],
    "7": [pop11_rule32,],
    "8": [pop11_rule32,],
    "9": [pop11_rule32,],
    ":": [pop11_rule9, pop11_rule20,],
    ";": [pop11_rule1, pop11_rule17,],
    "<": [pop11_rule24, pop11_rule25, pop11_rule27,],
    "=": [pop11_rule22,],
    ">": [pop11_rule11, pop11_rule23, pop11_rule26,],
    "@": [pop11_rule19, pop11_rule32,],
    "A": [pop11_rule32,],
    "B": [pop11_rule32,],
    "C": [pop11_rule32,],
    "D": [pop11_rule32,],
    "E": [pop11_rule32,],
    "F": [pop11_rule32,],
    "G": [pop11_rule32,],
    "H": [pop11_rule32,],
    "I": [pop11_rule32,],
    "J": [pop11_rule32,],
    "K": [pop11_rule32,],
    "L": [pop11_rule32,],
    "M": [pop11_rule32,],
    "N": [pop11_rule32,],
    "O": [pop11_rule32,],
    "P": [pop11_rule32,],
    "Q": [pop11_rule32,],
    "R": [pop11_rule32,],
    "S": [pop11_rule32,],
    "T": [pop11_rule32,],
    "U": [pop11_rule32,],
    "V": [pop11_rule32,],
    "W": [pop11_rule32,],
    "X": [pop11_rule32,],
    "Y": [pop11_rule32,],
    "Z": [pop11_rule32,],
    "[": [pop11_rule5,],
    "^": [pop11_rule18,],
    "_": [pop11_rule32,],
    "`": [pop11_rule4,],
    "a": [pop11_rule32,],
    "b": [pop11_rule32,],
    "c": [pop11_rule32,],
    "d": [pop11_rule32,],
    "e": [pop11_rule32,],
    "f": [pop11_rule32,],
    "g": [pop11_rule32,],
    "h": [pop11_rule32,],
    "i": [pop11_rule32,],
    "j": [pop11_rule32,],
    "k": [pop11_rule32,],
    "l": [pop11_rule32,],
    "m": [pop11_rule32,],
    "n": [pop11_rule32,],
    "o": [pop11_rule32,],
    "p": [pop11_rule32,],
    "q": [pop11_rule32,],
    "r": [pop11_rule32,],
    "s": [pop11_rule32,],
    "t": [pop11_rule32,],
    "u": [pop11_rule32,],
    "v": [pop11_rule32,],
    "w": [pop11_rule32,],
    "x": [pop11_rule32,],
    "y": [pop11_rule32,],
    "z": [pop11_rule32,],
    "{": [pop11_rule6,],
    "|": [pop11_rule21,],
}

# Rules for pop11_list ruleset.

def pop11_rule33(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="[", end="]",
          delegate="pop11::list")

def pop11_rule34(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="{", end="}",
          delegate="pop11::list")

def pop11_rule35(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="![", end="]",
          delegate="pop11::list")

def pop11_rule36(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="pop11::string",
          no_line_break=True)

def pop11_rule37(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="pop11::string",
          no_line_break=True)

def pop11_rule38(colorer, s, i):
    return colorer.match_span(s, i, kind="null", begin="%", end="%",
          delegate="pop11::main")

def pop11_rule39(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/",
          delegate="pop11::comment")

def pop11_rule40(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";;;")

def pop11_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal2", seq="=")

def pop11_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal2", seq="==")

def pop11_rule43(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern="^")

def pop11_rule44(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern="?")

# Rules dict for pop11_list ruleset.
rulesDict2 = {
    "!": [pop11_rule35,],
    "\"": [pop11_rule37,],
    "%": [pop11_rule38,],
    "'": [pop11_rule36,],
    "/": [pop11_rule39,],
    ";": [pop11_rule40,],
    "=": [pop11_rule41, pop11_rule42,],
    "?": [pop11_rule44,],
    "[": [pop11_rule33,],
    "^": [pop11_rule43,],
    "{": [pop11_rule34,],
}

# Rules for pop11_string ruleset.

# Rules dict for pop11_string ruleset.
rulesDict3 = {}

# Rules for pop11_comment ruleset.

def pop11_rule45(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":")

def pop11_rule46(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment1", seq="*")

# Rules dict for pop11_comment ruleset.
rulesDict4 = {
    "*": [pop11_rule46,],
    ":": [pop11_rule45,],
}

# x.rulesDictDict for pop11 mode.
rulesDictDict = {
    "pop11_comment": rulesDict4,
    "pop11_list": rulesDict2,
    "pop11_main": rulesDict1,
    "pop11_string": rulesDict3,
}

# Import dict for pop11 mode.
importDict = {}
