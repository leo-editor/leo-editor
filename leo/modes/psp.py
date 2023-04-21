# Leo colorizer control file for psp mode.
# This file is in the public domain.

# Properties for psp mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

# Attributes dict for psp_main ruleset.
psp_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for psp_tags ruleset.
psp_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for psp_directive ruleset.
psp_directive_attributes_dict = {
    "default": "LITERAL4",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for psp mode.
attributesDictDict = {
    "psp_directive": psp_directive_attributes_dict,
    "psp_main": psp_main_attributes_dict,
    "psp_tags": psp_tags_attributes_dict,
}

# Keywords dict for psp_main ruleset.
psp_main_keywords_dict = {}

# Keywords dict for psp_tags ruleset.
psp_tags_keywords_dict = {}

# Keywords dict for psp_directive ruleset.
psp_directive_keywords_dict = {
    "file": "keyword4",
    "include": "keyword4",
}

# Dictionary of keywords dictionaries for psp mode.
keywordsDictDict = {
    "psp_directive": psp_directive_keywords_dict,
    "psp_main": psp_main_keywords_dict,
    "psp_tags": psp_tags_keywords_dict,
}

# Rules for psp_main ruleset.

def psp_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="literal4", begin="<%@", end="%>",
          delegate="psp::directive")

def psp_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="<%--", end="--%>")

def psp_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="<%", end="%>",
          delegate="python::main")

def psp_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"jscript\">", end="</script>",
          delegate="javascript::main")

def psp_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script language=\"javascript\">", end="</script>",
          delegate="javascript::main")

def psp_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script>", end="</script>",
          delegate="javascript::main")

def psp_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<!--#", end="-->")

def psp_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def psp_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE>", end="</STYLE>",
          delegate="css::main")

def psp_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="psp::tags")

def psp_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for psp_main ruleset.
rulesDict1 = {
    "&": [psp_rule10,],
    "<": [psp_rule0, psp_rule1, psp_rule2, psp_rule3, psp_rule4, psp_rule5, psp_rule6, psp_rule7, psp_rule8, psp_rule9,],
}

# Rules for psp_tags ruleset.

def psp_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def psp_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def psp_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def psp_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="<%--", end="--%>")

def psp_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="<%", end="%>",
          delegate="python::main")

# Rules dict for psp_tags ruleset.
rulesDict2 = {
    "\"": [psp_rule11,],
    "'": [psp_rule12,],
    "<": [psp_rule14, psp_rule15,],
    "=": [psp_rule13,],
}

# Rules for psp_directive ruleset.

def psp_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def psp_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def psp_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def psp_rule19(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for psp_directive ruleset.
rulesDict3 = {
    "\"": [psp_rule16,],
    "'": [psp_rule17,],
    "0": [psp_rule19,],
    "1": [psp_rule19,],
    "2": [psp_rule19,],
    "3": [psp_rule19,],
    "4": [psp_rule19,],
    "5": [psp_rule19,],
    "6": [psp_rule19,],
    "7": [psp_rule19,],
    "8": [psp_rule19,],
    "9": [psp_rule19,],
    "=": [psp_rule18,],
    "@": [psp_rule19,],
    "A": [psp_rule19,],
    "B": [psp_rule19,],
    "C": [psp_rule19,],
    "D": [psp_rule19,],
    "E": [psp_rule19,],
    "F": [psp_rule19,],
    "G": [psp_rule19,],
    "H": [psp_rule19,],
    "I": [psp_rule19,],
    "J": [psp_rule19,],
    "K": [psp_rule19,],
    "L": [psp_rule19,],
    "M": [psp_rule19,],
    "N": [psp_rule19,],
    "O": [psp_rule19,],
    "P": [psp_rule19,],
    "Q": [psp_rule19,],
    "R": [psp_rule19,],
    "S": [psp_rule19,],
    "T": [psp_rule19,],
    "U": [psp_rule19,],
    "V": [psp_rule19,],
    "W": [psp_rule19,],
    "X": [psp_rule19,],
    "Y": [psp_rule19,],
    "Z": [psp_rule19,],
    "a": [psp_rule19,],
    "b": [psp_rule19,],
    "c": [psp_rule19,],
    "d": [psp_rule19,],
    "e": [psp_rule19,],
    "f": [psp_rule19,],
    "g": [psp_rule19,],
    "h": [psp_rule19,],
    "i": [psp_rule19,],
    "j": [psp_rule19,],
    "k": [psp_rule19,],
    "l": [psp_rule19,],
    "m": [psp_rule19,],
    "n": [psp_rule19,],
    "o": [psp_rule19,],
    "p": [psp_rule19,],
    "q": [psp_rule19,],
    "r": [psp_rule19,],
    "s": [psp_rule19,],
    "t": [psp_rule19,],
    "u": [psp_rule19,],
    "v": [psp_rule19,],
    "w": [psp_rule19,],
    "x": [psp_rule19,],
    "y": [psp_rule19,],
    "z": [psp_rule19,],
}

# x.rulesDictDict for psp mode.
rulesDictDict = {
    "psp_directive": rulesDict3,
    "psp_main": rulesDict1,
    "psp_tags": rulesDict2,
}

# Import dict for psp mode.
importDict = {}
