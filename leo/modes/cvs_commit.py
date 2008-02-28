# Leo colorizer control file for cvs_commit mode.
# This file is in the public domain.

# Properties for cvs_commit mode.
properties = {}

# Attributes dict for cvs_commit_main ruleset.
cvs_commit_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "false",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Attributes dict for cvs_commit_changed ruleset.
cvs_commit_changed_attributes_dict = {
	"default": "COMMENT2",
	"digit_re": "",
	"escape": "",
	"highlight_digits": "false",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for cvs_commit mode.
attributesDictDict = {
	"cvs_commit_changed": cvs_commit_changed_attributes_dict,
	"cvs_commit_main": cvs_commit_main_attributes_dict,
}

# Keywords dict for cvs_commit_main ruleset.
cvs_commit_main_keywords_dict = {}

# Keywords dict for cvs_commit_changed ruleset.
cvs_commit_changed_keywords_dict = {}

# Dictionary of keywords dictionaries for cvs_commit mode.
keywordsDictDict = {
	"cvs_commit_changed": cvs_commit_changed_keywords_dict,
	"cvs_commit_main": cvs_commit_main_keywords_dict,
}

# Rules for cvs_commit_main ruleset.

def cvs_commit_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="CVS:",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="cvs_commit::changed", exclude_match=False)

# Rules dict for cvs_commit_main ruleset.
rulesDict1 = {
	"C": [cvs_commit_rule0,],
}

# Rules for cvs_commit_changed ruleset.

def cvs_commit_rule1(colorer, s, i):
    return colorer.match_seq(s, i, kind="comment1", seq="CVS:",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def cvs_commit_rule2(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword1", seq="Committing in",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def cvs_commit_rule3(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword1", seq="Added Files:",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def cvs_commit_rule4(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword1", seq="Modified Files:",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def cvs_commit_rule5(colorer, s, i):
    return colorer.match_seq(s, i, kind="keyword1", seq="Removed Files:",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for cvs_commit_changed ruleset.
rulesDict2 = {
	"A": [cvs_commit_rule3,],
	"C": [cvs_commit_rule1,cvs_commit_rule2,],
	"M": [cvs_commit_rule4,],
	"R": [cvs_commit_rule5,],
}

# x.rulesDictDict for cvs_commit mode.
rulesDictDict = {
	"cvs_commit_changed": rulesDict2,
	"cvs_commit_main": rulesDict1,
}

# Import dict for cvs_commit mode.
importDict = {}

