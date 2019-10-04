# Leo colorizer control file for asciidoc mode.
# This file is in the public domain.

# Important: this file is based on md.py.
#                  Much more work is needed.

# Properties for asciidoc mode.
# Important: most of this file is actually an html colorizer.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
    "indentSize": "4",
    "maxLineLen": "120",
    "tabSize": "4",
}

# Attributes dict for asciidoc_main ruleset.
asciidoc_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for asciidoc_inline_markup ruleset.
asciidoc_inline_markup_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for asciidoc_block_html_tags ruleset.
asciidoc_block_html_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for asciidoc_markdown ruleset.
asciidoc_markdown_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for asciidoc_link_label_definition ruleset.
asciidoc_link_label_definition_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for asciidoc_link_inline_url_title ruleset.
asciidoc_link_inline_url_title_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for asciidoc_link_inline_url_title_close ruleset.
asciidoc_link_inline_url_title_close_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for asciidoc_link_inline_label_close ruleset.
asciidoc_link_inline_label_close_attributes_dict = {
    "default": "LABEL",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for asciidoc_markdown_blockquote ruleset.
asciidoc_markdown_blockquote_attributes_dict = {
    "default": "LABEL",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for asciidoc mode.
attributesDictDict = {
    "asciidoc_block_html_tags": asciidoc_block_html_tags_attributes_dict,
    "asciidoc_inline_markup": asciidoc_inline_markup_attributes_dict,
    "asciidoc_link_inline_label_close": asciidoc_link_inline_label_close_attributes_dict,
    "asciidoc_link_inline_url_title": asciidoc_link_inline_url_title_attributes_dict,
    "asciidoc_link_inline_url_title_close": asciidoc_link_inline_url_title_close_attributes_dict,
    "asciidoc_link_label_definition": asciidoc_link_label_definition_attributes_dict,
    "asciidoc_main": asciidoc_main_attributes_dict,
    "asciidoc_markdown": asciidoc_markdown_attributes_dict,
    "asciidoc_markdown_blockquote": asciidoc_markdown_blockquote_attributes_dict,
}

# Keywords dict for asciidoc_main ruleset.
asciidoc_main_keywords_dict = {}

# Keywords dict for asciidoc_inline_markup ruleset.
asciidoc_inline_markup_keywords_dict = {}

# Keywords dict for asciidoc_block_html_tags ruleset.
asciidoc_block_html_tags_keywords_dict = {}

# Keywords dict for asciidoc_markdown ruleset.
asciidoc_markdown_keywords_dict = {}

# Keywords dict for asciidoc_link_label_definition ruleset.
asciidoc_link_label_definition_keywords_dict = {}

# Keywords dict for asciidoc_link_inline_url_title ruleset.
asciidoc_link_inline_url_title_keywords_dict = {}

# Keywords dict for asciidoc_link_inline_url_title_close ruleset.
asciidoc_link_inline_url_title_close_keywords_dict = {}

# Keywords dict for asciidoc_link_inline_label_close ruleset.
asciidoc_link_inline_label_close_keywords_dict = {}

# Keywords dict for asciidoc_markdown_blockquote ruleset.
asciidoc_markdown_blockquote_keywords_dict = {}

# Dictionary of keywords dictionaries for asciidoc mode.
keywordsDictDict = {
    "asciidoc_block_html_tags": asciidoc_block_html_tags_keywords_dict,
    "asciidoc_inline_markup": asciidoc_inline_markup_keywords_dict,
    "asciidoc_link_inline_label_close": asciidoc_link_inline_label_close_keywords_dict,
    "asciidoc_link_inline_url_title": asciidoc_link_inline_url_title_keywords_dict,
    "asciidoc_link_inline_url_title_close": asciidoc_link_inline_url_title_close_keywords_dict,
    "asciidoc_link_label_definition": asciidoc_link_label_definition_keywords_dict,
    "asciidoc_main": asciidoc_main_keywords_dict,
    "asciidoc_markdown": asciidoc_markdown_keywords_dict,
    "asciidoc_markdown_blockquote": asciidoc_markdown_blockquote_keywords_dict,
}

# Rules for asciidoc_main ruleset.

def asciidoc_heading(colorer,s,i):
    # issue 386.
    # print('asciidoc_heading',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="^[#]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_link(colorer,s,i):
    # issue 386.
    # print('asciidoc_link',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="\[[^]]+\]\([^)]+\)",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_star_emphasis1(colorer,s,i):
    # issue 386.
    # print('asciidoc_underscore_emphasis1',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="\\*[^\\s*][^*]*\\*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_star_emphasis2(colorer,s,i):
    # issue 386.
    # print('asciidoc_star_emphasis2',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="\\*\\*[^*]+\\*\\*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_underscore_emphasis1(colorer,s,i):
    # issue 386.
    # print('asciidoc_underscore_emphasis1',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="_[^_]+_",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_underline_equals(colorer,s,i):
    # issue 386.
    # print('asciidoc_underline_equals',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="^===[=]+$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")
        
def asciidoc_underline_minus(colorer,s,i):
    # issue 386.
    # print('asciidoc_underline_minus',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="---[-]+$",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_underscore_emphasis2(colorer,s,i):
    # issue 386.
    # print('asciidoc_underscore_emphasis2',i)
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="__[^_]+__",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<script", end="</script>",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="html::javascript",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule2(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="<hr\\b([^<>])*?/?>",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule3(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="markup", begin="<(p|div|h[1-6]|blockquote|pre|table|dl|ol|ul|noscript|form|fieldset|iframe|math|ins|del)\\b", end="</$1>",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::block_html_tags",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule4(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq=" < ",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::inline_markup",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)


# Rules dict for asciidoc_main ruleset.
rulesDict1 = {
    "#": [asciidoc_heading,], # Issue #386.
    "[": [asciidoc_link,], # issue 386.
    "*": [asciidoc_star_emphasis2, asciidoc_star_emphasis1,], # issue 386. Order important
    "=": [asciidoc_underline_equals,], # issue 386.
    "-": [asciidoc_underline_minus,], # issue 386.
    "_": [asciidoc_underscore_emphasis2, asciidoc_underscore_emphasis1,], # issue 386. Order important.
    " ": [asciidoc_rule4,],
    "<": [asciidoc_rule0,asciidoc_rule1,asciidoc_rule2,asciidoc_rule3,asciidoc_rule5,],
}

# Rules for asciidoc_inline_markup ruleset.


# Rules dict for asciidoc_inline_markup ruleset.
rulesDict2 = {}

# Rules for asciidoc_block_html_tags ruleset.

if 0: # Rules 6 & 7 will never match?

    def asciidoc_rule6(colorer, s, i):
        return colorer.match_eol_span_regexp(s, i, kind="invalid", regexp="[\\S]+",
            at_line_start=True, at_whitespace_end=False, at_word_start=False,
            delegate="", exclude_match=False)

    def asciidoc_rule7(colorer, s, i):
        return colorer.match_eol_span_regexp(s, i, kind="invalid", regexp="{1,3}[\\S]+",
            at_line_start=True, at_whitespace_end=False, at_word_start=False,
            delegate="", exclude_match=False)

def asciidoc_rule8(colorer, s, i):
    # leadin: [ \t]
    return colorer.match_eol_span_regexp(s, i, kind="", regexp="( {4}|\\t)",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="html::main", exclude_match=False)

def asciidoc_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for asciidoc_block_html_tags ruleset.
rulesDict3 = {
    " ": [asciidoc_rule8], # new
    "\t":[asciidoc_rule8], # new
    "\"": [asciidoc_rule9,],
    "'": [asciidoc_rule10,],
    # "(": [asciidoc_rule8,],
    "=": [asciidoc_rule11,],
    # "[": [asciidoc_rule6,], # Will never fire: the leadin character is any non-space!
    # "{": [asciidoc_rule7,], # Will never fire: the leading character is any non-space!
}

# Rules for asciidoc_markdown ruleset.

def asciidoc_rule12(colorer, s, i):
    # Leadins: [ \t>]
    return colorer.match_eol_span_regexp(s, i, kind="", regexp="[ \\t]*(>[ \\t]{1})+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::markdown_blockquote", exclude_match=False)

def asciidoc_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule14(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="_",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule15(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="\\][",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule16(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="``` ruby", end="```",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="ruby::main",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="```", end="```",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule19(colorer, s, i):
    # leadin: `
    return colorer.match_span_regexp(s, i, kind="literal2", begin="(`{1,2})", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule20(colorer, s, i):
    # Leadins are [ \t]
    return colorer.match_eol_span_regexp(s, i, kind="literal2", regexp="( {4,}|\\t+)\\S",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def asciidoc_rule21(colorer, s, i):
    # Leadins are [=-]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[=-]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def asciidoc_rule22(colorer, s, i):
    # Leadin is #
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="#{1,6}[ \\t]*(.+?)",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def asciidoc_rule23(colorer, s, i):
    # Leadins are [ \t -_*]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[ ]{0,2}([ ]?[-_*][ ]?){3,}[ \\t]*",
        at_line_start=True, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def asciidoc_rule24(colorer, s, i):
    # Leadins are [ \t*+-]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}[*+-][ \\t]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule25(colorer, s, i):
    # Leadins are [ \t0123456789]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}\\d+\\.[ \\t]+",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule26(colorer, s, i):
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="\\[(.*?)\\]\\:",
        at_line_start=False, at_whitespace_end=True, at_word_start=False,
        delegate="asciidoc::link_label_definition", exclude_match=False)

def asciidoc_rule27(colorer, s, i):
    # leadin: [
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="!?\\[[\\p{Alnum}\\p{Blank}]*", end="\\]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::link_inline_url_title",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def asciidoc_rule28(colorer, s, i):
    # Leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal3", begin="(\\*\\*|__)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def asciidoc_rule29(colorer, s, i):
    # Leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal4", begin="(\\*|_)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

# Rules dict for asciidoc_markdown ruleset.
rulesDict4 = {
# Existing leadins...
    "!": [asciidoc_rule27,],
    "#": [asciidoc_rule22,],
    "*": [asciidoc_rule13,asciidoc_rule23,asciidoc_rule24,asciidoc_rule28,asciidoc_rule29], # new: 23,24,28,29.
    "\\": [asciidoc_rule15,asciidoc_rule16,asciidoc_rule26,],
    "_": [asciidoc_rule14,asciidoc_rule23,asciidoc_rule24,asciidoc_rule28,asciidoc_rule29], # new: 23,24,28,29.
    "`": [asciidoc_rule17,asciidoc_rule18,asciidoc_rule19,], # new: 19
    "[": [asciidoc_rule27,], # new: 27 old: 12,21,23,24,25.
# Unused leadins...
    # "(": [asciidoc_rule28,asciidoc_rule29,],
# New leadins...
    " ": [asciidoc_rule12,asciidoc_rule20,asciidoc_rule23,asciidoc_rule24,asciidoc_rule25,],
    "\t":[asciidoc_rule12,asciidoc_rule20,asciidoc_rule23,asciidoc_rule24,asciidoc_rule25],
    ">":[asciidoc_rule12,],
    "=":[asciidoc_rule21,],
    "-":[asciidoc_rule21,asciidoc_rule23,asciidoc_rule24],
    "0":[asciidoc_rule25,],
    "1":[asciidoc_rule25,],
    "2":[asciidoc_rule25,],
    "3":[asciidoc_rule25,],
    "4":[asciidoc_rule25,],
    "5":[asciidoc_rule25,],
    "6":[asciidoc_rule25,],
    "7":[asciidoc_rule25,],
    "8":[asciidoc_rule25,],
    "9":[asciidoc_rule25,],
}

# Rules for asciidoc_link_label_definition ruleset.

def asciidoc_rule30(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule31(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule32(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="(",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule33(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=")",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

# Rules dict for asciidoc_link_label_definition ruleset.
rulesDict5 = {
    "\"": [asciidoc_rule31,],
    "(": [asciidoc_rule32,],
    ")": [asciidoc_rule33,],
    "\\": [asciidoc_rule30,],
}

# Rules for asciidoc_link_inline_url_title ruleset.

def asciidoc_rule34(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule35(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="\\[", end="\\]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::link_inline_label_close",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def asciidoc_rule36(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="\\(", end="\\)",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::link_inline_url_title_close",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

# Rules dict for asciidoc_link_inline_url_title ruleset.
rulesDict6 = {
    "(": [asciidoc_rule36,],
    "[": [asciidoc_rule35,],
    "]": [asciidoc_rule34,],
}

# Rules for asciidoc_link_inline_url_title_close ruleset.

def asciidoc_rule37(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq=")",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::main", exclude_match=False)

# Rules dict for asciidoc_link_inline_url_title_close ruleset.
rulesDict7 = {
    ")": [asciidoc_rule37,],
}

# Rules for asciidoc_link_inline_label_close ruleset.

def asciidoc_rule38(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="null", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::main", exclude_match=False)

# Rules dict for asciidoc_link_inline_label_close ruleset.
rulesDict8 = {
    "]": [asciidoc_rule38,],
}

# Rules for asciidoc_markdown_blockquote ruleset.

def asciidoc_rule39(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq=" < ",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule40(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::inline_markup",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule41(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule42(colorer, s, i):
    return colorer.match_seq(s, i, kind="null", seq="_",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule43(colorer, s, i):
    # leadin: backslash.
    return colorer.match_seq(s, i, kind="null", seq="\\][",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule44(colorer, s, i):
    # leadin: backslash.
    return colorer.match_seq_regexp(s, i, kind="null", regexp="\\\\[\\Q*_\\`[](){}#+.!-\\E]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule45(colorer, s, i):
    # leadin: `
    return colorer.match_span_regexp(s, i, kind="literal2", begin="(`{1,2})", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule46(colorer, s, i):
    # leadins: [ \t]
    return colorer.match_eol_span_regexp(s, i, kind="literal2", regexp="( {4,}|\\t+)\\S",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def asciidoc_rule47(colorer, s, i):
    # leadins: [=-]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[=-]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def asciidoc_rule48(colorer, s, i):
    # leadin: #
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="#{1,6}[ \\t]*(.+?)",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def asciidoc_rule49(colorer, s, i):
    # leadins: [ -_*]
    return colorer.match_eol_span_regexp(s, i, kind="keyword1", regexp="[ ]{0,2}([ ]?[-_*][ ]?){3,}[ \\t]*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def asciidoc_rule50(colorer, s, i):
    # leadins: [ \t*+-]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}[*+-][ \\t]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule51(colorer, s, i):
    # leadins: [ \t0123456789]
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="[ \\t]{0,}\\d+\\.[ \\t]+",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def asciidoc_rule52(colorer, s, i):
    # leadin: [
    return colorer.match_eol_span_regexp(s, i, kind="label", regexp="\\[(.*?)\\]\\:",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::link_label_definition", exclude_match=False)

def asciidoc_rule53(colorer, s, i):
    # leadin: [
    return colorer.match_span_regexp(s, i, kind="keyword4", begin="!?\\[[\\p{Alnum}\\p{Blank}]*", end="\\]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="asciidoc::link_inline_url_title",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def asciidoc_rule54(colorer, s, i):
    # leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal3", begin="(\\*\\*|__)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def asciidoc_rule55(colorer, s, i):
     # leadins: [*_]
    return colorer.match_span_regexp(s, i, kind="literal4", begin="(\\*|_)", end="$1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

# Rules dict for asciidoc_markdown_blockquote ruleset.
rulesDict9 = {
# old, unused.
# "!": [], # 53
# "[": [], # 47,49,50,51,
    " ": [asciidoc_rule39,asciidoc_rule46,asciidoc_rule49,asciidoc_rule50], # new: 46,49,50
    "\t":[asciidoc_rule46,asciidoc_rule50,], # new: 46,50
    "#": [asciidoc_rule48,],
    "(": [asciidoc_rule54,asciidoc_rule55,], # 45,46
    "*": [asciidoc_rule41,asciidoc_rule49,asciidoc_rule50,asciidoc_rule54,asciidoc_rule55,], # new: 49,50,54,55
    "<": [asciidoc_rule40,],
    "\\": [asciidoc_rule43,asciidoc_rule44,], # 52,53
    "_": [asciidoc_rule42,asciidoc_rule49,asciidoc_rule54,asciidoc_rule55,], # new: 49,54,55 
# new leadins:
    "+":[asciidoc_rule50,],
    "-":[asciidoc_rule47,asciidoc_rule49,asciidoc_rule50,],
    "=":[asciidoc_rule47,],
    "[":[asciidoc_rule52,asciidoc_rule53],
    "`":[asciidoc_rule45,],
    "0":[asciidoc_rule50,],
    "1":[asciidoc_rule50,],
    "2":[asciidoc_rule50,],
    "3":[asciidoc_rule50,],
    "4":[asciidoc_rule50,],
    "5":[asciidoc_rule50,],
    "6":[asciidoc_rule50,],
    "7":[asciidoc_rule50,],
    "8":[asciidoc_rule50,],
    "9":[asciidoc_rule50,],
}

# x.rulesDictDict for asciidoc mode.
rulesDictDict = {
    "asciidoc_block_html_tags": rulesDict3,
    "asciidoc_inline_markup": rulesDict2,
    "asciidoc_link_inline_label_close": rulesDict8,
    "asciidoc_link_inline_url_title": rulesDict6,
    "asciidoc_link_inline_url_title_close": rulesDict7,
    "asciidoc_link_label_definition": rulesDict5,
    "asciidoc_main": rulesDict1,
    "asciidoc_markdown": rulesDict4,
    "asciidoc_markdown_blockquote": rulesDict9,
}

# Import dict for asciidoc mode.
importDict = {
    "asciidoc_inline_markup": ["html::tags",],
    "asciidoc_link_label_definition": ["asciidoc_link_label_definition::markdown",],
    "asciidoc_main": ["asciidoc_main::markdown",],
}

