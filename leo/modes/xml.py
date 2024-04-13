# Leo colorizer control file for xml mode.
# This file is in the public domain.

# Properties for xml mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

# Attributes dict for xml_main ruleset.
xml_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for xml_tags ruleset.
xml_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "-_",
}

# Attributes dict for xml_dtd_tags ruleset.
xml_dtd_tags_attributes_dict = {
    "default": "KEYWORD2",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "-_",
}

# Attributes dict for xml_entity_tags ruleset.
xml_entity_tags_attributes_dict = {
    "default": "KEYWORD2",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "-_",
}

# Attributes dict for xml_cdata ruleset.
xml_cdata_attributes_dict = {
    "default": "COMMENT2",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "-_",
}

# Dictionary of attributes dictionaries for xml mode.
attributesDictDict = {
    "xml_cdata": xml_cdata_attributes_dict,
    "xml_dtd_tags": xml_dtd_tags_attributes_dict,
    "xml_entity_tags": xml_entity_tags_attributes_dict,
    "xml_main": xml_main_attributes_dict,
    "xml_tags": xml_tags_attributes_dict,
}

# Keywords dict for xml_main ruleset.
xml_main_keywords_dict = {}

# Keywords dict for xml_tags ruleset.
xml_tags_keywords_dict = {}

# Keywords dict for xml_dtd_tags ruleset.
xml_dtd_tags_keywords_dict = {
    "#IMPLIED": "keyword1",
    "#PCDATA": "keyword1",
    "#REQUIRED": "keyword1",
    "CDATA": "keyword1",
    "EMPTY": "keyword1",
    "IGNORE": "keyword1",
    "INCLUDE": "keyword1",
    "NDATA": "keyword1",
}

# Keywords dict for xml_entity_tags ruleset.
xml_entity_tags_keywords_dict = {
    "SYSTEM": "keyword1",
}

# Keywords dict for xml_cdata ruleset.
xml_cdata_keywords_dict = {}

# Dictionary of keywords dictionaries for xml mode.
keywordsDictDict = {
    "xml_cdata": xml_cdata_keywords_dict,
    "xml_dtd_tags": xml_dtd_tags_keywords_dict,
    "xml_entity_tags": xml_entity_tags_keywords_dict,
    "xml_main": xml_main_keywords_dict,
    "xml_tags": xml_tags_keywords_dict,
}

# Rules for xml_main ruleset.

def xml_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def xml_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!ENTITY", end=">",
          delegate="xml::entity-tags")

def xml_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<![CDATA[", end="]]>",
          delegate="xml::cdata")

def xml_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
          delegate="xml::dtd-tags")

def xml_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="<?", end=">")

def xml_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="xml::tags")

def xml_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for xml_main ruleset.
rulesDict1 = {
    "&": [xml_rule6,],
    "<": [xml_rule0, xml_rule1, xml_rule2, xml_rule3, xml_rule4, xml_rule5,],
}

# Rules for xml_tags ruleset.

def xml_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def xml_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def xml_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def xml_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="/")

def xml_rule11(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          exclude_match=True)

def xml_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

# Rules dict for xml_tags ruleset.
rulesDict2 = {
    "\"": [xml_rule8,],
    "'": [xml_rule9,],
    "/": [xml_rule10,],
    ":": [xml_rule11, xml_rule12,],
    "<": [xml_rule7,],
}

# Rules for xml_dtd_tags ruleset.

def xml_rule13(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def xml_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="--", end="--")

def xml_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="%", end=";",
          no_word_break=True)

def xml_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def xml_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def xml_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="[", end="]",
          delegate="xml::main")

def xml_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def xml_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def xml_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def xml_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def xml_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def xml_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def xml_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def xml_rule26(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for xml_dtd_tags ruleset.
rulesDict3 = {
    "\"": [xml_rule16,],
    "#": [xml_rule26,],
    "%": [xml_rule15,],
    "'": [xml_rule17,],
    "(": [xml_rule19,],
    ")": [xml_rule20,],
    "*": [xml_rule23,],
    "+": [xml_rule24,],
    ",": [xml_rule25,],
    "-": [xml_rule14,],
    "0": [xml_rule26,],
    "1": [xml_rule26,],
    "2": [xml_rule26,],
    "3": [xml_rule26,],
    "4": [xml_rule26,],
    "5": [xml_rule26,],
    "6": [xml_rule26,],
    "7": [xml_rule26,],
    "8": [xml_rule26,],
    "9": [xml_rule26,],
    "<": [xml_rule13,],
    "?": [xml_rule22,],
    "@": [xml_rule26,],
    "A": [xml_rule26,],
    "B": [xml_rule26,],
    "C": [xml_rule26,],
    "D": [xml_rule26,],
    "E": [xml_rule26,],
    "F": [xml_rule26,],
    "G": [xml_rule26,],
    "H": [xml_rule26,],
    "I": [xml_rule26,],
    "J": [xml_rule26,],
    "K": [xml_rule26,],
    "L": [xml_rule26,],
    "M": [xml_rule26,],
    "N": [xml_rule26,],
    "O": [xml_rule26,],
    "P": [xml_rule26,],
    "Q": [xml_rule26,],
    "R": [xml_rule26,],
    "S": [xml_rule26,],
    "T": [xml_rule26,],
    "U": [xml_rule26,],
    "V": [xml_rule26,],
    "W": [xml_rule26,],
    "X": [xml_rule26,],
    "Y": [xml_rule26,],
    "Z": [xml_rule26,],
    "[": [xml_rule18,],
    "a": [xml_rule26,],
    "b": [xml_rule26,],
    "c": [xml_rule26,],
    "d": [xml_rule26,],
    "e": [xml_rule26,],
    "f": [xml_rule26,],
    "g": [xml_rule26,],
    "h": [xml_rule26,],
    "i": [xml_rule26,],
    "j": [xml_rule26,],
    "k": [xml_rule26,],
    "l": [xml_rule26,],
    "m": [xml_rule26,],
    "n": [xml_rule26,],
    "o": [xml_rule26,],
    "p": [xml_rule26,],
    "q": [xml_rule26,],
    "r": [xml_rule26,],
    "s": [xml_rule26,],
    "t": [xml_rule26,],
    "u": [xml_rule26,],
    "v": [xml_rule26,],
    "w": [xml_rule26,],
    "x": [xml_rule26,],
    "y": [xml_rule26,],
    "z": [xml_rule26,],
    "|": [xml_rule21,],
}

# Rules for xml_entity_tags ruleset.

def xml_rule27(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def xml_rule28(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="--", end="--")

def xml_rule29(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def xml_rule30(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def xml_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def xml_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def xml_rule33(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for xml_entity_tags ruleset.
rulesDict4 = {
    "\"": [xml_rule29,],
    "#": [xml_rule33,],
    "%": [xml_rule32,],
    "'": [xml_rule30,],
    "-": [xml_rule28,],
    "0": [xml_rule33,],
    "1": [xml_rule33,],
    "2": [xml_rule33,],
    "3": [xml_rule33,],
    "4": [xml_rule33,],
    "5": [xml_rule33,],
    "6": [xml_rule33,],
    "7": [xml_rule33,],
    "8": [xml_rule33,],
    "9": [xml_rule33,],
    "<": [xml_rule27,],
    "=": [xml_rule31,],
    "@": [xml_rule33,],
    "A": [xml_rule33,],
    "B": [xml_rule33,],
    "C": [xml_rule33,],
    "D": [xml_rule33,],
    "E": [xml_rule33,],
    "F": [xml_rule33,],
    "G": [xml_rule33,],
    "H": [xml_rule33,],
    "I": [xml_rule33,],
    "J": [xml_rule33,],
    "K": [xml_rule33,],
    "L": [xml_rule33,],
    "M": [xml_rule33,],
    "N": [xml_rule33,],
    "O": [xml_rule33,],
    "P": [xml_rule33,],
    "Q": [xml_rule33,],
    "R": [xml_rule33,],
    "S": [xml_rule33,],
    "T": [xml_rule33,],
    "U": [xml_rule33,],
    "V": [xml_rule33,],
    "W": [xml_rule33,],
    "X": [xml_rule33,],
    "Y": [xml_rule33,],
    "Z": [xml_rule33,],
    "a": [xml_rule33,],
    "b": [xml_rule33,],
    "c": [xml_rule33,],
    "d": [xml_rule33,],
    "e": [xml_rule33,],
    "f": [xml_rule33,],
    "g": [xml_rule33,],
    "h": [xml_rule33,],
    "i": [xml_rule33,],
    "j": [xml_rule33,],
    "k": [xml_rule33,],
    "l": [xml_rule33,],
    "m": [xml_rule33,],
    "n": [xml_rule33,],
    "o": [xml_rule33,],
    "p": [xml_rule33,],
    "q": [xml_rule33,],
    "r": [xml_rule33,],
    "s": [xml_rule33,],
    "t": [xml_rule33,],
    "u": [xml_rule33,],
    "v": [xml_rule33,],
    "w": [xml_rule33,],
    "x": [xml_rule33,],
    "y": [xml_rule33,],
    "z": [xml_rule33,],
}

# Rules for xml_cdata ruleset.

# Rules dict for xml_cdata ruleset.
rulesDict5 = {}

# x.rulesDictDict for xml mode.
rulesDictDict = {
    "xml_cdata": rulesDict5,
    "xml_dtd_tags": rulesDict3,
    "xml_entity_tags": rulesDict4,
    "xml_main": rulesDict1,
    "xml_tags": rulesDict2,
}

# Import dict for xml mode.
importDict = {}
