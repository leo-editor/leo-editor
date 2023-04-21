# Leo colorizer control file for zpt mode.
# This file is in the public domain.

# Properties for zpt mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

# Attributes dict for zpt_main ruleset.
zpt_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for zpt_tags ruleset.
zpt_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for zpt_attribute ruleset.
zpt_attribute_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for zpt_javascript ruleset.
zpt_javascript_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for zpt_back_to_html ruleset.
zpt_back_to_html_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for zpt_css ruleset.
zpt_css_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for zpt mode.
attributesDictDict = {
    "zpt_attribute": zpt_attribute_attributes_dict,
    "zpt_back_to_html": zpt_back_to_html_attributes_dict,
    "zpt_css": zpt_css_attributes_dict,
    "zpt_javascript": zpt_javascript_attributes_dict,
    "zpt_main": zpt_main_attributes_dict,
    "zpt_tags": zpt_tags_attributes_dict,
}

# Keywords dict for zpt_main ruleset.
zpt_main_keywords_dict = {}

# Keywords dict for zpt_tags ruleset.
zpt_tags_keywords_dict = {
    "attributes": "keyword3",
    "condition": "keyword3",
    "content": "keyword3",
    "define": "keyword3",
    "define-macro": "keyword3",
    "define-slot": "keyword3",
    "fill-slot": "keyword3",
    "metal": "keyword1",
    "omit-tag": "keyword3",
    "on-error": "keyword3",
    "repeat": "keyword3",
    "replace": "keyword3",
    "tal": "keyword1",
    "use-macro": "keyword3",
}

# Keywords dict for zpt_attribute ruleset.
zpt_attribute_keywords_dict = {
    "attrs": "literal3",
    "container": "literal3",
    "contexts": "literal3",
    "default": "literal3",
    "end": "literal3",
    "even": "literal3",
    "exists": "keyword4",
    "first": "literal3",
    "here": "literal3",
    "index": "literal3",
    "last": "literal3",
    "length": "literal3",
    "letter": "literal3",
    "modules": "literal3",
    "nocall": "keyword4",
    "not": "keyword4",
    "nothing": "literal3",
    "number": "literal3",
    "odd": "literal3",
    "options": "literal3",
    "path": "keyword4",
    "python": "keyword4",
    "repeat": "literal3",
    "request": "literal3",
    "roman": "literal3",
    "root": "literal3",
    "start": "literal3",
    "string": "keyword4",
    "template": "literal3",
    "user": "literal3",
}

# Keywords dict for zpt_javascript ruleset.
zpt_javascript_keywords_dict = {}

# Keywords dict for zpt_back_to_html ruleset.
zpt_back_to_html_keywords_dict = {}

# Keywords dict for zpt_css ruleset.
zpt_css_keywords_dict = {}

# Dictionary of keywords dictionaries for zpt mode.
keywordsDictDict = {
    "zpt_attribute": zpt_attribute_keywords_dict,
    "zpt_back_to_html": zpt_back_to_html_keywords_dict,
    "zpt_css": zpt_css_keywords_dict,
    "zpt_javascript": zpt_javascript_keywords_dict,
    "zpt_main": zpt_main_keywords_dict,
    "zpt_tags": zpt_tags_keywords_dict,
}

# Rules for zpt_main ruleset.

def zpt_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def zpt_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
          delegate="zpt::javascript")

def zpt_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
          delegate="zpt::css")

def zpt_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
          delegate="xml::dtd-tags")

def zpt_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="zpt::tags")

def zpt_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for zpt_main ruleset.
rulesDict1 = {
    "&": [zpt_rule5,],
    "<": [zpt_rule0, zpt_rule1, zpt_rule2, zpt_rule3, zpt_rule4,],
}

# Rules for zpt_tags ruleset.

def zpt_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="zpt::attribute")

def zpt_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="zpt::attribute")

def zpt_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def zpt_rule9(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for zpt_tags ruleset.
rulesDict2 = {
    "\"": [zpt_rule6,],
    "'": [zpt_rule7,],
    "-": [zpt_rule9,],
    "0": [zpt_rule9,],
    "1": [zpt_rule9,],
    "2": [zpt_rule9,],
    "3": [zpt_rule9,],
    "4": [zpt_rule9,],
    "5": [zpt_rule9,],
    "6": [zpt_rule9,],
    "7": [zpt_rule9,],
    "8": [zpt_rule9,],
    "9": [zpt_rule9,],
    "=": [zpt_rule8,],
    "@": [zpt_rule9,],
    "A": [zpt_rule9,],
    "B": [zpt_rule9,],
    "C": [zpt_rule9,],
    "D": [zpt_rule9,],
    "E": [zpt_rule9,],
    "F": [zpt_rule9,],
    "G": [zpt_rule9,],
    "H": [zpt_rule9,],
    "I": [zpt_rule9,],
    "J": [zpt_rule9,],
    "K": [zpt_rule9,],
    "L": [zpt_rule9,],
    "M": [zpt_rule9,],
    "N": [zpt_rule9,],
    "O": [zpt_rule9,],
    "P": [zpt_rule9,],
    "Q": [zpt_rule9,],
    "R": [zpt_rule9,],
    "S": [zpt_rule9,],
    "T": [zpt_rule9,],
    "U": [zpt_rule9,],
    "V": [zpt_rule9,],
    "W": [zpt_rule9,],
    "X": [zpt_rule9,],
    "Y": [zpt_rule9,],
    "Z": [zpt_rule9,],
    "a": [zpt_rule9,],
    "b": [zpt_rule9,],
    "c": [zpt_rule9,],
    "d": [zpt_rule9,],
    "e": [zpt_rule9,],
    "f": [zpt_rule9,],
    "g": [zpt_rule9,],
    "h": [zpt_rule9,],
    "i": [zpt_rule9,],
    "j": [zpt_rule9,],
    "k": [zpt_rule9,],
    "l": [zpt_rule9,],
    "m": [zpt_rule9,],
    "n": [zpt_rule9,],
    "o": [zpt_rule9,],
    "p": [zpt_rule9,],
    "q": [zpt_rule9,],
    "r": [zpt_rule9,],
    "s": [zpt_rule9,],
    "t": [zpt_rule9,],
    "u": [zpt_rule9,],
    "v": [zpt_rule9,],
    "w": [zpt_rule9,],
    "x": [zpt_rule9,],
    "y": [zpt_rule9,],
    "z": [zpt_rule9,],
}

# Rules for zpt_attribute ruleset.

def zpt_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def zpt_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def zpt_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def zpt_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def zpt_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal2", seq="$$")

def zpt_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          no_line_break=True)

def zpt_rule16(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$")

def zpt_rule17(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for zpt_attribute ruleset.
rulesDict3 = {
    "$": [zpt_rule14, zpt_rule15, zpt_rule16,],
    "-": [zpt_rule17,],
    "0": [zpt_rule17,],
    "1": [zpt_rule17,],
    "2": [zpt_rule17,],
    "3": [zpt_rule17,],
    "4": [zpt_rule17,],
    "5": [zpt_rule17,],
    "6": [zpt_rule17,],
    "7": [zpt_rule17,],
    "8": [zpt_rule17,],
    "9": [zpt_rule17,],
    ":": [zpt_rule10,],
    ";": [zpt_rule11,],
    "?": [zpt_rule12,],
    "@": [zpt_rule17,],
    "A": [zpt_rule17,],
    "B": [zpt_rule17,],
    "C": [zpt_rule17,],
    "D": [zpt_rule17,],
    "E": [zpt_rule17,],
    "F": [zpt_rule17,],
    "G": [zpt_rule17,],
    "H": [zpt_rule17,],
    "I": [zpt_rule17,],
    "J": [zpt_rule17,],
    "K": [zpt_rule17,],
    "L": [zpt_rule17,],
    "M": [zpt_rule17,],
    "N": [zpt_rule17,],
    "O": [zpt_rule17,],
    "P": [zpt_rule17,],
    "Q": [zpt_rule17,],
    "R": [zpt_rule17,],
    "S": [zpt_rule17,],
    "T": [zpt_rule17,],
    "U": [zpt_rule17,],
    "V": [zpt_rule17,],
    "W": [zpt_rule17,],
    "X": [zpt_rule17,],
    "Y": [zpt_rule17,],
    "Z": [zpt_rule17,],
    "a": [zpt_rule17,],
    "b": [zpt_rule17,],
    "c": [zpt_rule17,],
    "d": [zpt_rule17,],
    "e": [zpt_rule17,],
    "f": [zpt_rule17,],
    "g": [zpt_rule17,],
    "h": [zpt_rule17,],
    "i": [zpt_rule17,],
    "j": [zpt_rule17,],
    "k": [zpt_rule17,],
    "l": [zpt_rule17,],
    "m": [zpt_rule17,],
    "n": [zpt_rule17,],
    "o": [zpt_rule17,],
    "p": [zpt_rule17,],
    "q": [zpt_rule17,],
    "r": [zpt_rule17,],
    "s": [zpt_rule17,],
    "t": [zpt_rule17,],
    "u": [zpt_rule17,],
    "v": [zpt_rule17,],
    "w": [zpt_rule17,],
    "x": [zpt_rule17,],
    "y": [zpt_rule17,],
    "z": [zpt_rule17,],
    "|": [zpt_rule13,],
}

# Rules for zpt_javascript ruleset.

def zpt_rule18(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=">",
          delegate="javascript::main")

def zpt_rule19(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="SRC=",
          delegate="zpt::back_to_html")

# Rules dict for zpt_javascript ruleset.
rulesDict4 = {
    ">": [zpt_rule18,],
    "S": [zpt_rule19,],
}

# Rules for zpt_back_to_html ruleset.

def zpt_rule20(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=">",
          delegate="zpt::main")

# Rules dict for zpt_back_to_html ruleset.
rulesDict5 = {
    ">": [zpt_rule20,],
}

# Rules for zpt_css ruleset.

def zpt_rule21(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=">",
          delegate="css::main")

# Rules dict for zpt_css ruleset.
rulesDict6 = {
    ">": [zpt_rule21,],
}

# x.rulesDictDict for zpt mode.
rulesDictDict = {
    "zpt_attribute": rulesDict3,
    "zpt_back_to_html": rulesDict5,
    "zpt_css": rulesDict6,
    "zpt_javascript": rulesDict4,
    "zpt_main": rulesDict1,
    "zpt_tags": rulesDict2,
}

# Import dict for zpt mode.
importDict = {}
