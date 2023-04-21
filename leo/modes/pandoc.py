# Leo colorizer control file for pandoc mode.
# Based on md.py.
# This file is in the public domain.

# Properties for pandoc mode.
# Important: most of this file is actually an html colorizer.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
    "indentSize": "4",
    "maxLineLen": "120",
    "tabSize": "4",
}

# Attributes dict for pandoc_main ruleset.
pandoc_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for pandoc_inline_markup ruleset.
pandoc_inline_markup_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for pandoc_block_html_tags ruleset.
pandoc_block_html_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for pandoc_markdown ruleset.
pandoc_markdown_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for pandoc_link_label_definition ruleset.
pandoc_link_label_definition_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for pandoc_link_inline_url_title ruleset.
pandoc_link_inline_url_title_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for pandoc_link_inline_url_title_close ruleset.
pandoc_link_inline_url_title_close_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for pandoc_link_inline_label_close ruleset.
pandoc_link_inline_label_close_attributes_dict = {
    "default": "LABEL",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for pandoc_markdown_blockquote ruleset.
pandoc_markdown_blockquote_attributes_dict = {
    "default": "LABEL",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for pandoc mode.
attributesDictDict = {
    "pandoc_block_html_tags": pandoc_block_html_tags_attributes_dict,
    "pandoc_inline_markup": pandoc_inline_markup_attributes_dict,
    "pandoc_link_inline_label_close": pandoc_link_inline_label_close_attributes_dict,
    "pandoc_link_inline_url_title": pandoc_link_inline_url_title_attributes_dict,
    "pandoc_link_inline_url_title_close": pandoc_link_inline_url_title_close_attributes_dict,
    "pandoc_link_label_definition": pandoc_link_label_definition_attributes_dict,
    "pandoc_main": pandoc_main_attributes_dict,
    "pandoc_markdown": pandoc_markdown_attributes_dict,
    "pandoc_markdown_blockquote": pandoc_markdown_blockquote_attributes_dict,
}

# Keywords dict for pandoc_main ruleset.
pandoc_main_keywords_dict = {}

# Keywords dict for pandoc_inline_markup ruleset.
pandoc_inline_markup_keywords_dict = {}

# Keywords dict for pandoc_block_html_tags ruleset.
pandoc_block_html_tags_keywords_dict = {}

# Keywords dict for pandoc_markdown ruleset.
pandoc_markdown_keywords_dict = {}

# Keywords dict for pandoc_link_label_definition ruleset.
pandoc_link_label_definition_keywords_dict = {}

# Keywords dict for pandoc_link_inline_url_title ruleset.
pandoc_link_inline_url_title_keywords_dict = {}

# Keywords dict for pandoc_link_inline_url_title_close ruleset.
pandoc_link_inline_url_title_close_keywords_dict = {}

# Keywords dict for pandoc_link_inline_label_close ruleset.
pandoc_link_inline_label_close_keywords_dict = {}

# Keywords dict for pandoc_markdown_blockquote ruleset.
pandoc_markdown_blockquote_keywords_dict = {}

# Dictionary of keywords dictionaries for pandoc mode.
keywordsDictDict = {
    "pandoc_block_html_tags": pandoc_block_html_tags_keywords_dict,
    "pandoc_inline_markup": pandoc_inline_markup_keywords_dict,
    "pandoc_link_inline_label_close": pandoc_link_inline_label_close_keywords_dict,
    "pandoc_link_inline_url_title": pandoc_link_inline_url_title_keywords_dict,
    "pandoc_link_inline_url_title_close": pandoc_link_inline_url_title_close_keywords_dict,
    "pandoc_link_label_definition": pandoc_link_label_definition_keywords_dict,
    "pandoc_main": pandoc_main_keywords_dict,
    "pandoc_markdown": pandoc_markdown_keywords_dict,
    "pandoc_markdown_blockquote": pandoc_markdown_blockquote_keywords_dict,
}

# Rules for pandoc_main ruleset.

def pandoc_heading(colorer, s, i):
    # issue 386.
    # print('pandoc_heading',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"^[#]+")

def pandoc_link(colorer, s, i):
    # issue 386.
    # print('pandoc_link',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"\[[^]]+\]\([^)]+\)")

def pandoc_star_emphasis1(colorer, s, i):
    # issue 386.
    # print('pandoc_underscore_emphasis1',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"\\*[^\\s*][^*]*\\*")

def pandoc_star_emphasis2(colorer, s, i):
    # issue 386.
    # print('pandoc_star_emphasis2',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"\\*\\*[^*]+\\*\\*")

def pandoc_underscore_emphasis1(colorer, s, i):
    # issue 386.
    # print('pandoc_underscore_emphasis1',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"_[^_]+_")

def pandoc_underline_equals(colorer, s, i):
    # issue 386.
    # print('pandoc_underline_equals',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"^===[=]+$")

def pandoc_underline_minus(colorer, s, i):
    # issue 386.
    # print('pandoc_underline_minus',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"---[-]+$")

def pandoc_underscore_emphasis2(colorer, s, i):
    # issue 386.
    # print('pandoc_underscore_emphasis2',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp=r"__[^_]+__")

def pandoc_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def pandoc_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script", end="</script>",
          at_line_start=True,
          delegate="html::javascript")

def pandoc_rule2(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="<hr\\b([^<>])*?/?>",
          at_line_start=True)

def pandoc_rule3(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="markup", begin="<(p|div|h[1-6]|blockquote|pre|table|dl|ol|ul|noscript|form|fieldset|iframe|math|ins|del)\\b", end="</$1>",
          at_line_start=True,
          delegate="pandoc::block_html_tags")

def pandoc_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=" < ")

def pandoc_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="pandoc::inline_markup")


# Rules dict for pandoc_main ruleset.
rulesDict1 = {
    "#": [pandoc_heading,],  # Issue #386.
    "[": [pandoc_link,],  # issue 386.
    "*": [pandoc_star_emphasis2, pandoc_star_emphasis1,],  # issue 386. Order important
    "=": [pandoc_underline_equals,],  # issue 386.
    "-": [pandoc_underline_minus,],  # issue 386.
    "_": [pandoc_underscore_emphasis2, pandoc_underscore_emphasis1,],  # issue 386. Order important.
    " ": [pandoc_rule4,],
    "<": [pandoc_rule0, pandoc_rule1, pandoc_rule2, pandoc_rule3, pandoc_rule5,],
}

# Rules for pandoc_inline_markup ruleset.


# Rules dict for pandoc_inline_markup ruleset.
rulesDict2 = {}

# Rules for pandoc_block_html_tags ruleset.

if 0:  # Rules 6 & 7 will never match?

    def pandoc_rule6(colorer, s, i):
        return colorer.match_eol_span_regexp(s, i, kind="invalid", regexp="[\\S]+",
          at_line_start=True)

    def pandoc_rule7(colorer, s, i):
        return colorer.match_eol_span_regexp(s, i, kind="invalid", regexp="{1,3}[\\S]+",
          at_line_start=True)

def pandoc_rule8(colorer, s, i):
    # leadin: [ \t]
    return colorer.match_eol_span_regexp(s, i, kind="", regexp="( {4}|\\t)",
          at_line_start=True,
          delegate="html::main")

def pandoc_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def pandoc_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def pandoc_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

# Rules dict for pandoc_block_html_tags ruleset.
rulesDict3 = {
    " ": [pandoc_rule8],  # new
    "\t": [pandoc_rule8],  # new
    "\"": [pandoc_rule9,],
    "'": [pandoc_rule10,],
    # "(": [pandoc_rule8,],
    "=": [pandoc_rule11,],
    # "[": [pandoc_rule6,], # Will never fire: the leadin character is any non-space!
    # "{": [pandoc_rule7,], # Will never fire: the leading character is any non-space!
}

# Rules for pandoc_markdown ruleset.

def pandoc_rule12(colorer, s, i):
    # Leadins: [ \t>]
    return colorer.match_eol_span_regexp(s, i, kind="", regexp="[ \\t]*(>[ \\t]{1})+",
          at_line_start=True,
          delegate="pandoc::markdown_blockquote")

def pandoc_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="*")

def pandoc_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="_")

def pandoc_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="\\][")

def pandoc_rule16(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]")

def pandoc_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="``` ruby", end="```",
          at_line_start=True,
          delegate="ruby::main")

def pandoc_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="```", end="```",
          at_line_start=True)

def pandoc_rule19(colorer, s, i):
    # leadin: `
    return colorer.match_span_regexp(s, i, kind="literal2", begin="(`{1,2})", end="$1")

def pandoc_rule20(colorer, s, i):
    # Leadins are [ \t]
    return colorer.match_eol_span_regexp(s, i, kind="literal2", regexp="( {4,}|\\t+)\\S",
          at_line_start=True)

def pandoc_rule21(colorer, s, i):
    # Leadins are [=-]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[=-]+",
          at_line_start=True)

def pandoc_rule22(colorer, s, i):
    # Leadin is #
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="#{1,6}[ \\t]*(.+?)",
          at_line_start=True)

def pandoc_rule23(colorer, s, i):
    # Leadins are [ \t -_*]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[ ]{0,2}([ ]?[-_*][ ]?){3,}[ \\t]*",
          at_line_start=True)

def pandoc_rule24(colorer, s, i):
    # Leadins are [ \t*+-]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}[*+-][ \\t]+",
          at_line_start=True)

def pandoc_rule25(colorer, s, i):
    # Leadins are [ \t0123456789]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}\\d+\\.[ \\t]+",
          at_line_start=True)

def pandoc_rule26(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="\\[(.*?)\\]\\:",
          at_whitespace_end=True,
          delegate="pandoc::link_label_definition")

def pandoc_rule27(colorer, s, i):
    # leadin: [
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="!?\\[[\\p{Alnum}\\p{Blank}]*", end="\\]",
          delegate="pandoc::link_inline_url_title",
          no_line_break=True)

def pandoc_rule28(colorer, s, i):
    # Leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal3", begin="(\\*\\*|__)", end="$1",
          no_line_break=True)

def pandoc_rule29(colorer, s, i):
    # Leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal4", begin="(\\*|_)", end="$1",
          no_line_break=True)

# Rules dict for pandoc_markdown ruleset.
rulesDict4 = {
# Existing leadins...
    "!": [pandoc_rule27,],
    "#": [pandoc_rule22,],
    "*": [pandoc_rule13, pandoc_rule23, pandoc_rule24, pandoc_rule28, pandoc_rule29],  # new: 23,24,28,29.
    "\\": [pandoc_rule15, pandoc_rule16, pandoc_rule26,],
    "_": [pandoc_rule14, pandoc_rule23, pandoc_rule24, pandoc_rule28, pandoc_rule29],  # new: 23,24,28,29.
    "`": [pandoc_rule17, pandoc_rule18, pandoc_rule19,],  # new: 19
    "[": [pandoc_rule27,],  # new: 27 old: 12,21,23,24,25.
# Unused leadins...
    # "(": [pandoc_rule28,pandoc_rule29,],
# New leadins...
    " ": [pandoc_rule12, pandoc_rule20, pandoc_rule23, pandoc_rule24, pandoc_rule25,],
    "\t": [pandoc_rule12, pandoc_rule20, pandoc_rule23, pandoc_rule24, pandoc_rule25],
    ">": [pandoc_rule12,],
    "=": [pandoc_rule21,],
    "-": [pandoc_rule21, pandoc_rule23, pandoc_rule24],
    "0": [pandoc_rule25,],
    "1": [pandoc_rule25,],
    "2": [pandoc_rule25,],
    "3": [pandoc_rule25,],
    "4": [pandoc_rule25,],
    "5": [pandoc_rule25,],
    "6": [pandoc_rule25,],
    "7": [pandoc_rule25,],
    "8": [pandoc_rule25,],
    "9": [pandoc_rule25,],
}

# Rules for pandoc_link_label_definition ruleset.

def pandoc_rule30(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]")

def pandoc_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="\"")

def pandoc_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def pandoc_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

# Rules dict for pandoc_link_label_definition ruleset.
rulesDict5 = {
    "\"": [pandoc_rule31,],
    "(": [pandoc_rule32,],
    ")": [pandoc_rule33,],
    "\\": [pandoc_rule30,],
}

# Rules for pandoc_link_inline_url_title ruleset.

def pandoc_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def pandoc_rule35(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="\\[", end="\\]",
          delegate="pandoc::link_inline_label_close",
          no_line_break=True)

def pandoc_rule36(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="\\(", end="\\)",
          delegate="pandoc::link_inline_url_title_close",
          no_line_break=True)

# Rules dict for pandoc_link_inline_url_title ruleset.
rulesDict6 = {
    "(": [pandoc_rule36,],
    "[": [pandoc_rule35,],
    "]": [pandoc_rule34,],
}

# Rules for pandoc_link_inline_url_title_close ruleset.

def pandoc_rule37(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq=")",
          delegate="pandoc::main")

# Rules dict for pandoc_link_inline_url_title_close ruleset.
rulesDict7 = {
    ")": [pandoc_rule37,],
}

# Rules for pandoc_link_inline_label_close ruleset.

def pandoc_rule38(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq="]",
          delegate="pandoc::main")

# Rules dict for pandoc_link_inline_label_close ruleset.
rulesDict8 = {
    "]": [pandoc_rule38,],
}

# Rules for pandoc_markdown_blockquote ruleset.

def pandoc_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=" < ")

def pandoc_rule40(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="pandoc::inline_markup")

def pandoc_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="*")

def pandoc_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="_")

def pandoc_rule43(colorer, s, i):
    # leadin: backslash.
    return colorer.match_plain_seq(s, i, kind="null", seq="\\][")

def pandoc_rule44(colorer, s, i):
    # leadin: backslash.
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]")

def pandoc_rule45(colorer, s, i):
    # leadin: `
    return colorer.match_span_regexp(s, i, kind="literal2", begin="(`{1,2})", end="$1")

def pandoc_rule46(colorer, s, i):
    # leadins: [ \t]
    return colorer.match_eol_span_regexp(s, i, kind="literal2", regexp="( {4,}|\\t+)\\S")

def pandoc_rule47(colorer, s, i):
    # leadins: [=-]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[=-]+")

def pandoc_rule48(colorer, s, i):
    # leadin: #
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="#{1,6}[ \\t]*(.+?)")

def pandoc_rule49(colorer, s, i):
    # leadins: [ -_*]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[ ]{0,2}([ ]?[-_*][ ]?){3,}[ \\t]*")

def pandoc_rule50(colorer, s, i):
    # leadins: [ \t*+-]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}[*+-][ \\t]+")

def pandoc_rule51(colorer, s, i):
    # leadins: [ \t0123456789]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}\\d+\\.[ \\t]+")

def pandoc_rule52(colorer, s, i):
    # leadin: [
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="\\[(.*?)\\]\\:",
          delegate="pandoc::link_label_definition")

def pandoc_rule53(colorer, s, i):
    # leadin: [
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="!?\\[[\\p{Alnum}\\p{Blank}]*", end="\\]",
          delegate="pandoc::link_inline_url_title",
          no_line_break=True)

def pandoc_rule54(colorer, s, i):
    # leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal3", begin="(\\*\\*|__)", end="$1")

def pandoc_rule55(colorer, s, i):
     # leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal4", begin="(\\*|_)", end="$1")

# Rules dict for pandoc_markdown_blockquote ruleset.
rulesDict9 = {
# old, unused.
# "!": [], # 53
# "[": [], # 47,49,50,51,
    " ": [pandoc_rule39, pandoc_rule46, pandoc_rule49, pandoc_rule50],  # new: 46,49,50
    "\t": [pandoc_rule46, pandoc_rule50,],  # new: 46,50
    "#": [pandoc_rule48,],
    "(": [pandoc_rule54, pandoc_rule55,],  # 45,46
    "*": [pandoc_rule41, pandoc_rule49, pandoc_rule50, pandoc_rule54, pandoc_rule55,],  # new: 49,50,54,55
    "<": [pandoc_rule40,],
    "\\": [pandoc_rule43, pandoc_rule44,],  # 52,53
    "_": [pandoc_rule42, pandoc_rule49, pandoc_rule54, pandoc_rule55,],  # new: 49,54,55
# new leadins:
    "+": [pandoc_rule50,],
    "-": [pandoc_rule47, pandoc_rule49, pandoc_rule50,],
    "=": [pandoc_rule47,],
    "[": [pandoc_rule52, pandoc_rule53],
    "`": [pandoc_rule45,],
    "0": [pandoc_rule50,],
    "1": [pandoc_rule50,],
    "2": [pandoc_rule50,],
    "3": [pandoc_rule50,],
    "4": [pandoc_rule50,],
    "5": [pandoc_rule50,],
    "6": [pandoc_rule50,],
    "7": [pandoc_rule50,],
    "8": [pandoc_rule50,],
    "9": [pandoc_rule50,],
}

# x.rulesDictDict for pandoc mode.
rulesDictDict = {
    "pandoc_block_html_tags": rulesDict3,
    "pandoc_inline_markup": rulesDict2,
    "pandoc_link_inline_label_close": rulesDict8,
    "pandoc_link_inline_url_title": rulesDict6,
    "pandoc_link_inline_url_title_close": rulesDict7,
    "pandoc_link_label_definition": rulesDict5,
    "pandoc_main": rulesDict1,
    "pandoc_markdown": rulesDict4,
    "pandoc_markdown_blockquote": rulesDict9,
}

# Import dict for pandoc mode.
importDict = {
    "pandoc_inline_markup": ["html::tags",],
    "pandoc_link_label_definition": ["pandoc_link_label_definition::markdown",],
    "pandoc_main": ["pandoc_main::markdown",],
}
