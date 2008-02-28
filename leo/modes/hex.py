# Leo colorizer control file for hex mode.
# This file is in the public domain.

# Properties for hex mode.
properties = {}

# Attributes dict for hex_main ruleset.
hex_main_attributes_dict = {
	"default": "LITERAL1",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for hex mode.
attributesDictDict = {
	"hex_main": hex_main_attributes_dict,
}

# Keywords dict for hex_main ruleset.
hex_main_keywords_dict = {}

# Dictionary of keywords dictionaries for hex mode.
keywordsDictDict = {
	"hex_main": hex_main_keywords_dict,
}

# Rules for hex_main ruleset.

def hex_rule0(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="keyword1", pattern=":",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def hex_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

# Rules dict for hex_main ruleset.
rulesDict1 = {
	":": [hex_rule0,],
	";": [hex_rule1,],
}

# x.rulesDictDict for hex mode.
rulesDictDict = {
	"hex_main": rulesDict1,
}

# Import dict for hex mode.
importDict = {}

