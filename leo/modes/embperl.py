# Leo colorizer control file for embperl mode.
# This file is in the public domain.

# Properties for embperl mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

# Attributes dict for embperl_main ruleset.
embperl_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for embperl mode.
attributesDictDict = {
    "embperl_main": embperl_main_attributes_dict,
}

# Keywords dict for embperl_main ruleset.
embperl_main_keywords_dict = {}

# Dictionary of keywords dictionaries for embperl mode.
keywordsDictDict = {
    "embperl_main": embperl_main_keywords_dict,
}

# Rules for embperl_main ruleset.

def embperl_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="[#", end="#]")

def embperl_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="[+", end="+]",
          delegate="perl::main")

def embperl_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="[-", end="-]",
          delegate="perl::main")

def embperl_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="[$", end="$]",
          delegate="perl::main")

def embperl_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="[!", end="!]",
          delegate="perl::main")


# Rules dict for embperl_main ruleset.
rulesDict1 = {
    "[": [embperl_rule0, embperl_rule1, embperl_rule2, embperl_rule3, embperl_rule4,],
}

# x.rulesDictDict for embperl mode.
rulesDictDict = {
    "embperl_main": rulesDict1,
}

# Import dict for embperl mode.
importDict = {
    "embperl_main": ["html::main",],
}
