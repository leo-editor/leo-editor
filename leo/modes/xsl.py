# Leo colorizer control file for xsl mode.
# This file is in the public domain.

# pylint: disable=fixme

# Properties for xsl mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
}

# Attributes dict for xsl_main ruleset.
xsl_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for xsl_tasks ruleset.
xsl_tasks_attributes_dict = {
    "default": "COMMENT1",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for xsl_tags ruleset.
xsl_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": ".-_:",
}

# Attributes dict for xsl_avt ruleset.
xsl_avt_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": ".-_:",
}

# Attributes dict for xsl_xsltags ruleset.
xsl_xsltags_attributes_dict = {
    "default": "KEYWORD2",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": ".-_:",
}

# Attributes dict for xsl_xpath ruleset.
xsl_xpath_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "[[:digit:]]+([[:punct:]][[:digit:]]+)?",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": ".-_",
}

# Attributes dict for xsl_xpathcomment2 ruleset.
xsl_xpathcomment2_attributes_dict = {
    "default": "COMMENT2",
    "digit_re": "[[:digit:]]+([[:punct:]][[:digit:]]+)?",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": ".-_",
}

# Attributes dict for xsl_xpathcomment3 ruleset.
xsl_xpathcomment3_attributes_dict = {
    "default": "COMMENT3",
    "digit_re": "[[:digit:]]+([[:punct:]][[:digit:]]+)?",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": ".-_",
}

# Dictionary of attributes dictionaries for xsl mode.
attributesDictDict = {
    "xsl_avt": xsl_avt_attributes_dict,
    "xsl_main": xsl_main_attributes_dict,
    "xsl_tags": xsl_tags_attributes_dict,
    "xsl_tasks": xsl_tasks_attributes_dict,
    "xsl_xpath": xsl_xpath_attributes_dict,
    "xsl_xpathcomment2": xsl_xpathcomment2_attributes_dict,
    "xsl_xpathcomment3": xsl_xpathcomment3_attributes_dict,
    "xsl_xsltags": xsl_xsltags_attributes_dict,
}

# Keywords dict for xsl_main ruleset.
xsl_main_keywords_dict = {}

# Keywords dict for xsl_tasks ruleset.
xsl_tasks_keywords_dict = {
    "???": "comment4",
    "DEBUG:": "comment4",
    "DONE:": "comment4",
    "FIXME:": "comment4",
    "IDEA:": "comment4",
    "NOTE:": "comment4",
    "QUESTION:": "comment4",
    "TODO:": "comment4",
    "XXX": "comment4",
}

# Keywords dict for xsl_tags ruleset.
xsl_tags_keywords_dict = {}

# Keywords dict for xsl_avt ruleset.
xsl_avt_keywords_dict = {}

# Keywords dict for xsl_xsltags ruleset.
xsl_xsltags_keywords_dict = {
    "analyze-string": "keyword1",
    "apply-imports": "keyword1",
    "apply-templates": "keyword1",
    "attribute": "keyword1",
    "attribute-set": "keyword1",
    "call-template": "keyword1",
    "character-map": "keyword1",
    "choose": "keyword1",
    "comment": "keyword1",
    "copy": "keyword1",
    "copy-of": "keyword1",
    "date-format": "keyword1",
    "decimal-format": "keyword1",
    "element": "keyword1",
    "fallback": "keyword1",
    "for-each": "keyword1",
    "for-each-group": "keyword1",
    "function": "keyword1",
    "if": "keyword1",
    "import": "keyword1",
    "import-schema": "keyword1",
    "include": "keyword1",
    "key": "keyword1",
    "matching-substring": "keyword1",
    "message": "keyword1",
    "namespace": "keyword1",
    "namespace-alias": "keyword1",
    "next-match": "keyword1",
    "non-matching-substring": "keyword1",
    "number": "keyword1",
    "otherwise": "keyword1",
    "output": "keyword1",
    "output-character": "keyword1",
    "param": "keyword1",
    "preserve-space": "keyword1",
    "processing-instruction": "keyword1",
    "result-document": "keyword1",
    "sequence": "keyword1",
    "sort": "keyword1",
    "sort-key": "keyword1",
    "strip-space": "keyword1",
    "stylesheet": "keyword1",
    "template": "keyword1",
    "text": "keyword1",
    "transform": "keyword1",
    "value-of": "keyword1",
    "variable": "keyword1",
    "when": "keyword1",
    "with-param": "keyword1",
}

# Keywords dict for xsl_xpath ruleset.
xsl_xpath_keywords_dict = {
    "-": "operator",
    "and": "operator",
    "as": "operator",
    "castable": "operator",
    "div": "operator",
    "else": "operator",
    "eq": "operator",
    "every": "operator",
    "except": "operator",
    "for": "operator",
    "ge": "operator",
    "gt": "operator",
    "idiv": "operator",
    "if": "operator",
    "in": "operator",
    "instance": "operator",
    "intersect": "operator",
    "is": "operator",
    "isnot": "operator",
    "le": "operator",
    "lt": "operator",
    "mod": "operator",
    "ne": "operator",
    "nillable": "operator",
    "of": "operator",
    "or": "operator",
    "return": "operator",
    "satisfies": "operator",
    "some": "operator",
    "then": "operator",
    "to": "operator",
    "treat": "operator",
    "union": "operator",
}

# Keywords dict for xsl_xpathcomment2 ruleset.
xsl_xpathcomment2_keywords_dict = {}

# Keywords dict for xsl_xpathcomment3 ruleset.
xsl_xpathcomment3_keywords_dict = {}

# Dictionary of keywords dictionaries for xsl mode.
keywordsDictDict = {
    "xsl_avt": xsl_avt_keywords_dict,
    "xsl_main": xsl_main_keywords_dict,
    "xsl_tags": xsl_tags_keywords_dict,
    "xsl_tasks": xsl_tasks_keywords_dict,
    "xsl_xpath": xsl_xpath_keywords_dict,
    "xsl_xpathcomment2": xsl_xpathcomment2_keywords_dict,
    "xsl_xpathcomment3": xsl_xpathcomment3_keywords_dict,
    "xsl_xsltags": xsl_xsltags_keywords_dict,
}

# Rules for xsl_main ruleset.

def xsl_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
          delegate="xsl::tasks")

def xsl_rule1(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="<(?=xsl:)", end=">",
          delegate="xsl::xsltags")

def xsl_rule2(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="<(?=/xsl:)", end=">",
          delegate="xsl::xsltags")

def xsl_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<![CDATA[", end="]]>",
          delegate="xml::cdata")

def xsl_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
          delegate="xml::dtd-tags")

def xsl_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="&", end=";",
          no_word_break=True)

def xsl_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="<?", end="?>")

def xsl_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="xsl::tags")

# Rules dict for xsl_main ruleset.
rulesDict1 = {
    "&": [xsl_rule5,],
    "<": [xsl_rule0, xsl_rule1, xsl_rule2, xsl_rule3, xsl_rule4, xsl_rule6, xsl_rule7,],
}

# Rules for xsl_tasks ruleset.

def xsl_rule8(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for xsl_tasks ruleset.
rulesDict2 = {
    "-": [xsl_rule8,],
    "0": [xsl_rule8,],
    "1": [xsl_rule8,],
    "2": [xsl_rule8,],
    "3": [xsl_rule8,],
    "4": [xsl_rule8,],
    "5": [xsl_rule8,],
    "6": [xsl_rule8,],
    "7": [xsl_rule8,],
    "8": [xsl_rule8,],
    "9": [xsl_rule8,],
    ":": [xsl_rule8,],
    "?": [xsl_rule8,],
    "@": [xsl_rule8,],
    "A": [xsl_rule8,],
    "B": [xsl_rule8,],
    "C": [xsl_rule8,],
    "D": [xsl_rule8,],
    "E": [xsl_rule8,],
    "F": [xsl_rule8,],
    "G": [xsl_rule8,],
    "H": [xsl_rule8,],
    "I": [xsl_rule8,],
    "J": [xsl_rule8,],
    "K": [xsl_rule8,],
    "L": [xsl_rule8,],
    "M": [xsl_rule8,],
    "N": [xsl_rule8,],
    "O": [xsl_rule8,],
    "P": [xsl_rule8,],
    "Q": [xsl_rule8,],
    "R": [xsl_rule8,],
    "S": [xsl_rule8,],
    "T": [xsl_rule8,],
    "U": [xsl_rule8,],
    "V": [xsl_rule8,],
    "W": [xsl_rule8,],
    "X": [xsl_rule8,],
    "Y": [xsl_rule8,],
    "Z": [xsl_rule8,],
    "a": [xsl_rule8,],
    "b": [xsl_rule8,],
    "c": [xsl_rule8,],
    "d": [xsl_rule8,],
    "e": [xsl_rule8,],
    "f": [xsl_rule8,],
    "g": [xsl_rule8,],
    "h": [xsl_rule8,],
    "i": [xsl_rule8,],
    "j": [xsl_rule8,],
    "k": [xsl_rule8,],
    "l": [xsl_rule8,],
    "m": [xsl_rule8,],
    "n": [xsl_rule8,],
    "o": [xsl_rule8,],
    "p": [xsl_rule8,],
    "q": [xsl_rule8,],
    "r": [xsl_rule8,],
    "s": [xsl_rule8,],
    "t": [xsl_rule8,],
    "u": [xsl_rule8,],
    "v": [xsl_rule8,],
    "w": [xsl_rule8,],
    "x": [xsl_rule8,],
    "y": [xsl_rule8,],
    "z": [xsl_rule8,],
}

# Rules for xsl_tags ruleset.

def xsl_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="\"", end="\"",
          delegate="xsl::avt")

def xsl_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="'", end="'",
          delegate="xsl::avt")

def xsl_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="xmlns:")

def xsl_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="xmlns")

def xsl_rule13(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":")

# Rules dict for xsl_tags ruleset.
rulesDict3 = {
    "\"": [xsl_rule9,],
    "'": [xsl_rule10,],
    ":": [xsl_rule13,],
    "x": [xsl_rule11, xsl_rule12,],
}

# Rules for xsl_avt ruleset.

def xsl_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="", seq="{{")

def xsl_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="", seq="}}")

def xsl_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="{", end="}",
          delegate="xsl::xpath")

def xsl_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="&", end=";",
          no_word_break=True)

# Rules dict for xsl_avt ruleset.
rulesDict4 = {
    "&": [xsl_rule17,],
    "{": [xsl_rule14, xsl_rule16,],
    "}": [xsl_rule15,],
}

# Rules for xsl_xsltags ruleset.

def xsl_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="\"", end="\"",
          delegate="xsl::avt")

def xsl_rule19(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="'", end="'",
          delegate="xsl::avt")

def xsl_rule20(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="count[[:space:]]*=[[:space:]]*\"", end="\"",
          delegate="xsl::xpath")

def xsl_rule21(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="count[[:space:]]*=[[:space:]]*'", end="'",
          delegate="xsl::xpath")

def xsl_rule22(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="from[[:space:]]*=[[:space:]]*\"", end="\"",
          delegate="xsl::xpath")

def xsl_rule23(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="from[[:space:]]*=[[:space:]]*'", end="'",
          delegate="xsl::xpath")

def xsl_rule24(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="group-adjacent[[:space:]]*=[[:space:]]*\"", end="\"",
          delegate="xsl::xpath")

def xsl_rule25(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="group-adjacent[[:space:]]*=[[:space:]]*'", end="'",
          delegate="xsl::xpath")

def xsl_rule26(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="group-by[[:space:]]*=[[:space:]]*\"", end="\"",
          delegate="xsl::xpath")

def xsl_rule27(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="group-by[[:space:]]*=[[:space:]]*'", end="'",
          delegate="xsl::xpath")

def xsl_rule28(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="group-ending-with[[:space:]]*=[[:space:]]*\"", end="\"",
          delegate="xsl::xpath")

def xsl_rule29(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="group-ending-with[[:space:]]*=[[:space:]]*'", end="'",
          delegate="xsl::xpath")

def xsl_rule30(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="group-starting-with[[:space:]]*=[[:space:]]*\"", end="\"",
          delegate="xsl::xpath")

def xsl_rule31(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="group-starting-with[[:space:]]*=[[:space:]]*'", end="'",
          delegate="xsl::xpath")

def xsl_rule32(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="match[[:space:]]*=[[:space:]]*\"", end="\"",
          delegate="xsl::xpath")

def xsl_rule33(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="match[[:space:]]*=[[:space:]]*'", end="'",
          delegate="xsl::xpath")

def xsl_rule34(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="select[[:space:]]*=[[:space:]]*\"", end="\"",
          delegate="xsl::xpath")

def xsl_rule35(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="select[[:space:]]*=[[:space:]]*'", end="'",
          delegate="xsl::xpath")

def xsl_rule36(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="test[[:space:]]*=[[:space:]]*\"", end="\"",
          delegate="xsl::xpath")

def xsl_rule37(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="test[[:space:]]*=[[:space:]]*'", end="'",
          delegate="xsl::xpath")

def xsl_rule38(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="use[[:space:]]*=[[:space:]]*\"", end="\"",
          delegate="xsl::xpath")

def xsl_rule39(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="keyword2", begin="use[[:space:]]*=[[:space:]]*'", end="'",
          delegate="xsl::xpath")

def xsl_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="xmlns:")

def xsl_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="xmlns")

def xsl_rule42(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":")

def xsl_rule43(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for xsl_xsltags ruleset.
rulesDict5 = {
    "\"": [xsl_rule18,],
    "'": [xsl_rule19,],
    "-": [xsl_rule43,],
    "0": [xsl_rule43,],
    "1": [xsl_rule43,],
    "2": [xsl_rule43,],
    "3": [xsl_rule43,],
    "4": [xsl_rule43,],
    "5": [xsl_rule43,],
    "6": [xsl_rule43,],
    "7": [xsl_rule43,],
    "8": [xsl_rule43,],
    "9": [xsl_rule43,],
    ":": [xsl_rule42, xsl_rule43,],
    "?": [xsl_rule43,],
    "@": [xsl_rule43,],
    "A": [xsl_rule43,],
    "B": [xsl_rule43,],
    "C": [xsl_rule43,],
    "D": [xsl_rule43,],
    "E": [xsl_rule43,],
    "F": [xsl_rule43,],
    "G": [xsl_rule43,],
    "H": [xsl_rule43,],
    "I": [xsl_rule43,],
    "J": [xsl_rule43,],
    "K": [xsl_rule43,],
    "L": [xsl_rule43,],
    "M": [xsl_rule43,],
    "N": [xsl_rule43,],
    "O": [xsl_rule43,],
    "P": [xsl_rule43,],
    "Q": [xsl_rule43,],
    "R": [xsl_rule43,],
    "S": [xsl_rule43,],
    "T": [xsl_rule43,],
    "U": [xsl_rule43,],
    "V": [xsl_rule43,],
    "W": [xsl_rule43,],
    "X": [xsl_rule43,],
    "Y": [xsl_rule43,],
    "Z": [xsl_rule43,],
    "a": [xsl_rule43,],
    "b": [xsl_rule43,],
    "c": [xsl_rule20, xsl_rule21, xsl_rule43,],
    "d": [xsl_rule43,],
    "e": [xsl_rule43,],
    "f": [xsl_rule22, xsl_rule23, xsl_rule43,],
    "g": [xsl_rule24, xsl_rule25, xsl_rule26, xsl_rule27, xsl_rule28, xsl_rule29, xsl_rule30, xsl_rule31, xsl_rule43,],
    "h": [xsl_rule43,],
    "i": [xsl_rule43,],
    "j": [xsl_rule43,],
    "k": [xsl_rule43,],
    "l": [xsl_rule43,],
    "m": [xsl_rule32, xsl_rule33, xsl_rule43,],
    "n": [xsl_rule43,],
    "o": [xsl_rule43,],
    "p": [xsl_rule43,],
    "q": [xsl_rule43,],
    "r": [xsl_rule43,],
    "s": [xsl_rule34, xsl_rule35, xsl_rule43,],
    "t": [xsl_rule36, xsl_rule37, xsl_rule43,],
    "u": [xsl_rule38, xsl_rule39, xsl_rule43,],
    "v": [xsl_rule43,],
    "w": [xsl_rule43,],
    "x": [xsl_rule40, xsl_rule41, xsl_rule43,],
    "y": [xsl_rule43,],
    "z": [xsl_rule43,],
}

# Rules for xsl_xpath ruleset.

def xsl_rule44(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def xsl_rule45(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def xsl_rule46(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="(:", end=":)",
          delegate="xsl::xpathcomment2")

def xsl_rule47(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="keyword4", pattern="::")

def xsl_rule48(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword4", seq="@")

def xsl_rule49(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def xsl_rule50(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!=")

def xsl_rule51(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def xsl_rule52(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&gt;")

def xsl_rule53(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&lt;")

def xsl_rule54(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def xsl_rule55(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def xsl_rule56(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def xsl_rule57(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def xsl_rule58(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def xsl_rule59(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def xsl_rule60(colorer, s, i):
    return colorer.match_span(s, i, kind="operator", begin="[", end="]",
          delegate="xsl::xpath")

def xsl_rule61(colorer, s, i):
    return colorer.match_span(s, i, kind="literal3", begin="&", end=";",
          no_word_break=True)

def xsl_rule62(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":")

def xsl_rule63(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def xsl_rule64(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern="$")

def xsl_rule65(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for xsl_xpath ruleset.
rulesDict6 = {
    "!": [xsl_rule50,],
    "\"": [xsl_rule44,],
    "$": [xsl_rule64,],
    "&": [xsl_rule52, xsl_rule53, xsl_rule61,],
    "'": [xsl_rule45,],
    "(": [xsl_rule46, xsl_rule63,],
    "*": [xsl_rule56,],
    "+": [xsl_rule55,],
    ",": [xsl_rule59,],
    "-": [xsl_rule65,],
    "/": [xsl_rule57,],
    "0": [xsl_rule65,],
    "1": [xsl_rule65,],
    "2": [xsl_rule65,],
    "3": [xsl_rule65,],
    "4": [xsl_rule65,],
    "5": [xsl_rule65,],
    "6": [xsl_rule65,],
    "7": [xsl_rule65,],
    "8": [xsl_rule65,],
    "9": [xsl_rule65,],
    ":": [xsl_rule47, xsl_rule62, xsl_rule65,],
    "=": [xsl_rule49,],
    ">": [xsl_rule51,],
    "?": [xsl_rule54, xsl_rule65,],
    "@": [xsl_rule48, xsl_rule65,],
    "A": [xsl_rule65,],
    "B": [xsl_rule65,],
    "C": [xsl_rule65,],
    "D": [xsl_rule65,],
    "E": [xsl_rule65,],
    "F": [xsl_rule65,],
    "G": [xsl_rule65,],
    "H": [xsl_rule65,],
    "I": [xsl_rule65,],
    "J": [xsl_rule65,],
    "K": [xsl_rule65,],
    "L": [xsl_rule65,],
    "M": [xsl_rule65,],
    "N": [xsl_rule65,],
    "O": [xsl_rule65,],
    "P": [xsl_rule65,],
    "Q": [xsl_rule65,],
    "R": [xsl_rule65,],
    "S": [xsl_rule65,],
    "T": [xsl_rule65,],
    "U": [xsl_rule65,],
    "V": [xsl_rule65,],
    "W": [xsl_rule65,],
    "X": [xsl_rule65,],
    "Y": [xsl_rule65,],
    "Z": [xsl_rule65,],
    "[": [xsl_rule60,],
    "a": [xsl_rule65,],
    "b": [xsl_rule65,],
    "c": [xsl_rule65,],
    "d": [xsl_rule65,],
    "e": [xsl_rule65,],
    "f": [xsl_rule65,],
    "g": [xsl_rule65,],
    "h": [xsl_rule65,],
    "i": [xsl_rule65,],
    "j": [xsl_rule65,],
    "k": [xsl_rule65,],
    "l": [xsl_rule65,],
    "m": [xsl_rule65,],
    "n": [xsl_rule65,],
    "o": [xsl_rule65,],
    "p": [xsl_rule65,],
    "q": [xsl_rule65,],
    "r": [xsl_rule65,],
    "s": [xsl_rule65,],
    "t": [xsl_rule65,],
    "u": [xsl_rule65,],
    "v": [xsl_rule65,],
    "w": [xsl_rule65,],
    "x": [xsl_rule65,],
    "y": [xsl_rule65,],
    "z": [xsl_rule65,],
    "|": [xsl_rule58,],
}

# Rules for xsl_xpathcomment2 ruleset.

def xsl_rule66(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="(:", end=":)",
          delegate="xsl::xpathcomment3")

# Rules dict for xsl_xpathcomment2 ruleset.
rulesDict7 = {
    "(": [xsl_rule66,],
}

# Rules for xsl_xpathcomment3 ruleset.

def xsl_rule67(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="(:", end=":)",
          delegate="xsl::xpathcomment2")

# Rules dict for xsl_xpathcomment3 ruleset.
rulesDict8 = {
    "(": [xsl_rule67,],
}

# x.rulesDictDict for xsl mode.
rulesDictDict = {
    "xsl_avt": rulesDict4,
    "xsl_main": rulesDict1,
    "xsl_tags": rulesDict3,
    "xsl_tasks": rulesDict2,
    "xsl_xpath": rulesDict6,
    "xsl_xpathcomment2": rulesDict7,
    "xsl_xpathcomment3": rulesDict8,
    "xsl_xsltags": rulesDict5,
}

# Import dict for xsl mode.
importDict = {}
