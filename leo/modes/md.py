
# Leo colorizer control file for md mode.
# This file is in the public domain.

# Properties for md mode.
properties = {
	"commentEnd": "-->",
     "commentStart": "<!---"
}

# Attributes dict for md_main ruleset.
md_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "\\",
	"highlight_digits": "false",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for md mode.
attributesDictDict = {
	"md_main": md_main_attributes_dict,
}

# Keywords dict for md_main ruleset.
md_main_keywords_dict = {}

# Dictionary of keywords dictionaries for md mode.
keywordsDictDict = {
	"md_main": md_main_keywords_dict,
}

# Rules for md_main ruleset.

def md_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!---", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)


# Rules dict for md_main ruleset.
rulesDict1 = {
  "<": [md_rule0,],
}

# x.rulesDictDict for md mode.
rulesDictDict = {
	"md_main": rulesDict1,
}

# Import dict for md mode.
importDict = {}

