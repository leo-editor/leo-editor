# Leo colorizer control file for pseudoplain mode.
# This file is in the public domain.

# Properties for plain mode.
properties = {}

# Attributes dict for pseudoplain_main ruleset.
pseudoplain_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "\\",
	"highlight_digits": "false",
	"ignore_case": "true",
	"no_word_sep": "",
}

pseudoplain_interior_attributes_dict = {
	"default": "comment1",
	"digit_re": "",
	"escape": "\\",
	"highlight_digits": "false",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for plain mode.
attributesDictDict = {
	"pseudoplain_main": pseudoplain_main_attributes_dict,
	"pseudoplain_interior": pseudoplain_interior_attributes_dict,
}

# Keywords dict for pseudoplain_main ruleset.
pseudoplain_main_keywords_dict = {}

# Dictionary of keywords dictionaries for plain mode.
keywordsDictDict = {
	"pseudoplain_main": pseudoplain_main_keywords_dict,
}

# Rules for pseudoplain_main ruleset.

def pseudoplain_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="[[", end="]]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="pseudoplain_interior",exclude_match=True,
        no_escape=False, no_line_break=False, no_word_break=False)

# Rules dict for pseudoplain_main ruleset.
rulesDict1 = {
    "[": [pseudoplain_rule0,],
}

rulesDict2 = {}

# x.rulesDictDict for plain mode.
rulesDictDict = {
	"pseudoplain_main": rulesDict1,
	"pseodoplain_interior": rulesDict2,
}

# Import dict for plain mode.
importDict = {}
