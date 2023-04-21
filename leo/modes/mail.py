# Leo colorizer control file for mail mode.
# This file is in the public domain.

# Properties for mail mode.
properties = {
    "lineComment": ">",
    "noWordSep": "-_",
}

# Attributes dict for mail_main ruleset.
mail_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "-_:)",
}

# Attributes dict for mail_signature ruleset.
mail_signature_attributes_dict = {
    "default": "COMMENT2",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "-_:)",
}

# Attributes dict for mail_header ruleset.
mail_header_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "-_:)",
}

# Dictionary of attributes dictionaries for mail mode.
attributesDictDict = {
    "mail_header": mail_header_attributes_dict,
    "mail_main": mail_main_attributes_dict,
    "mail_signature": mail_signature_attributes_dict,
}

# Keywords dict for mail_main ruleset.
mail_main_keywords_dict = {}

# Keywords dict for mail_signature ruleset.
mail_signature_keywords_dict = {}

# Keywords dict for mail_header ruleset.
mail_header_keywords_dict = {}

# Dictionary of keywords dictionaries for mail mode.
keywordsDictDict = {
    "mail_header": mail_header_keywords_dict,
    "mail_main": mail_main_keywords_dict,
    "mail_signature": mail_signature_keywords_dict,
}

# Rules for mail_main ruleset.

def mail_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment3", seq=">>>",
          at_line_start=True)

def mail_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq=">>",
          at_line_start=True)

def mail_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=">",
          at_line_start=True)

def mail_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="|",
          at_line_start=True)

def mail_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=":",
          at_line_start=True)

def mail_rule5(colorer, s, i):
    return colorer.match_seq(s, i, kind="comment2", seq="--",
          at_line_start=True,
          delegate="mail::signature")

def mail_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq=":-)")

def mail_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq=":-(")

def mail_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq=":)")

def mail_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq=":(")

def mail_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq=";-)")

def mail_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq=";-(")

def mail_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq=";)")

def mail_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword1", seq=";(")

def mail_rule14(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_line_start=True)

# Rules dict for mail_main ruleset.
rulesDict1 = {
    "-": [mail_rule5,],
    ":": [mail_rule4, mail_rule6, mail_rule7, mail_rule8, mail_rule9, mail_rule14,],
    ";": [mail_rule10, mail_rule11, mail_rule12, mail_rule13,],
    ">": [mail_rule0, mail_rule1, mail_rule2,],
    "|": [mail_rule3,],
}

# Rules for mail_signature ruleset.

# Rules dict for mail_signature ruleset.
rulesDict2 = {}

# Rules for mail_header ruleset.

def mail_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<", end=">",
          no_line_break=True)

# Rules dict for mail_header ruleset.
rulesDict3 = {
    "<": [mail_rule15,],
}

# x.rulesDictDict for mail mode.
rulesDictDict = {
    "mail_header": rulesDict3,
    "mail_main": rulesDict1,
    "mail_signature": rulesDict2,
}

# Import dict for mail mode.
importDict = {}
