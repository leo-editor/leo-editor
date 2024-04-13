# Leo colorizer control file for sgml mode.
# This file is in the public domain.

# Properties for sgml mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

# Attributes dict for sgml_main ruleset.
sgml_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for sgml mode.
attributesDictDict = {
    "sgml_main": sgml_main_attributes_dict,
}

# Keywords dict for sgml_main ruleset.
sgml_main_keywords_dict = {}

# Dictionary of keywords dictionaries for sgml mode.
keywordsDictDict = {
    "sgml_main": sgml_main_keywords_dict,
}

# Rules for sgml_main ruleset.

def sgml_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def sgml_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!ENTITY", end=">",
          delegate="xml::entity-tags")

def sgml_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<![CDATA[", end="]]>",
          delegate="xml::cdata")

def sgml_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
          delegate="xml::dtd-tags")

def sgml_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="xml::tags")

def sgml_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for sgml_main ruleset.
rulesDict1 = {
    "&": [sgml_rule5,],
    "<": [sgml_rule0, sgml_rule1, sgml_rule2, sgml_rule3, sgml_rule4,],
}

# x.rulesDictDict for sgml mode.
rulesDictDict = {
    "sgml_main": rulesDict1,
}

# Import dict for sgml mode.
importDict = {}
