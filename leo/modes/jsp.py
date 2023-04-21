# Leo colorizer control file for jsp mode.
# This file is in the public domain.

# Properties for jsp mode.
properties = {
    "commentEnd": "--%>",
    "commentStart": "<%--",
}

# Attributes dict for jsp_main ruleset.
jsp_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for jsp_comment ruleset.
jsp_comment_attributes_dict = {
    "default": "COMMENT1",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for jsp_directives ruleset.
jsp_directives_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for jsp_tags ruleset.
jsp_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for jsp_attrvalue ruleset.
jsp_attrvalue_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for jsp mode.
attributesDictDict = {
    "jsp_attrvalue": jsp_attrvalue_attributes_dict,
    "jsp_comment": jsp_comment_attributes_dict,
    "jsp_directives": jsp_directives_attributes_dict,
    "jsp_main": jsp_main_attributes_dict,
    "jsp_tags": jsp_tags_attributes_dict,
}

# Keywords dict for jsp_main ruleset.
jsp_main_keywords_dict = {}

# Keywords dict for jsp_comment ruleset.
jsp_comment_keywords_dict = {}

# Keywords dict for jsp_directives ruleset.
jsp_directives_keywords_dict = {
    "autoflush": "keyword2",
    "buffer": "keyword2",
    "charset": "keyword2",
    "contenttype": "keyword2",
    "default": "keyword2",
    "errorpage": "keyword2",
    "extends": "keyword2",
    "file": "keyword2",
    "id": "keyword2",
    "import": "keyword2",
    "include": "keyword1",
    "info": "keyword2",
    "iserrorpage": "keyword2",
    "isthreadsafe": "keyword2",
    "language": "keyword2",
    "method": "keyword2",
    "name": "keyword2",
    "page": "keyword1",
    "prefix": "keyword2",
    "required": "keyword2",
    "rtexprvalue": "keyword2",
    "scope": "keyword2",
    "session": "keyword2",
    "tag": "keyword1",
    "tagattribute": "keyword1",
    "taglib": "keyword1",
    "tagvariable": "keyword1",
    "type": "keyword2",
    "uri": "keyword2",
}

# Keywords dict for jsp_tags ruleset.
jsp_tags_keywords_dict = {}

# Keywords dict for jsp_attrvalue ruleset.
jsp_attrvalue_keywords_dict = {}

# Dictionary of keywords dictionaries for jsp mode.
keywordsDictDict = {
    "jsp_attrvalue": jsp_attrvalue_keywords_dict,
    "jsp_comment": jsp_comment_keywords_dict,
    "jsp_directives": jsp_directives_keywords_dict,
    "jsp_main": jsp_main_keywords_dict,
    "jsp_tags": jsp_tags_keywords_dict,
}

# Rules for jsp_main ruleset.

def jsp_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="<%--", end="--%>")

def jsp_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<%@", end="%>",
          delegate="jsp::directives")

def jsp_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<jsp:directive>", end="</jsp:directive>",
          delegate="jsp::directives")

def jsp_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<%=", end="%>",
          delegate="java::main")

def jsp_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<jsp:expression>", end="</jsp:expression>",
          delegate="java::main")

def jsp_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<%!", end="%>",
          delegate="java::main")

def jsp_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<jsp:declaration>", end="</jsp:declaration>",
          delegate="java::main")

def jsp_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<%", end="%>",
          delegate="java::main")

def jsp_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<jsp:scriptlet>", end="</jsp:scriptlet>",
          delegate="java::main")

def jsp_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
          delegate="jsp::comment")

def jsp_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
          delegate="html::javascript")

def jsp_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
          delegate="html::css")

def jsp_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
          delegate="xml::dtd-tags")

def jsp_rule13(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="jsp::tags")

def jsp_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for jsp_main ruleset.
rulesDict1 = {
    "&": [jsp_rule14,],
    "<": [jsp_rule0, jsp_rule1, jsp_rule2, jsp_rule3, jsp_rule4, jsp_rule5, jsp_rule6, jsp_rule7, jsp_rule8, jsp_rule9, jsp_rule10, jsp_rule11, jsp_rule12, jsp_rule13,],
}

# Rules for jsp_comment ruleset.

def jsp_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="<%--", end="--%>")

def jsp_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<%=", end="%>",
          delegate="java::main")

def jsp_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<%", end="%>",
          delegate="java::main")

# Rules dict for jsp_comment ruleset.
rulesDict2 = {
    "<": [jsp_rule15, jsp_rule16, jsp_rule17,],
}

# Rules for jsp_directives ruleset.

def jsp_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<%=", end="%>",
          delegate="java::main")

def jsp_rule19(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="jsp::attrvalue")

def jsp_rule20(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="jsp::attrvalue")

def jsp_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="/")

def jsp_rule22(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          exclude_match=True)

def jsp_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def jsp_rule24(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for jsp_directives ruleset.
rulesDict3 = {
    "\"": [jsp_rule19,],
    "'": [jsp_rule20,],
    "/": [jsp_rule21,],
    "0": [jsp_rule24,],
    "1": [jsp_rule24,],
    "2": [jsp_rule24,],
    "3": [jsp_rule24,],
    "4": [jsp_rule24,],
    "5": [jsp_rule24,],
    "6": [jsp_rule24,],
    "7": [jsp_rule24,],
    "8": [jsp_rule24,],
    "9": [jsp_rule24,],
    ":": [jsp_rule22, jsp_rule23,],
    "<": [jsp_rule18,],
    "@": [jsp_rule24,],
    "A": [jsp_rule24,],
    "B": [jsp_rule24,],
    "C": [jsp_rule24,],
    "D": [jsp_rule24,],
    "E": [jsp_rule24,],
    "F": [jsp_rule24,],
    "G": [jsp_rule24,],
    "H": [jsp_rule24,],
    "I": [jsp_rule24,],
    "J": [jsp_rule24,],
    "K": [jsp_rule24,],
    "L": [jsp_rule24,],
    "M": [jsp_rule24,],
    "N": [jsp_rule24,],
    "O": [jsp_rule24,],
    "P": [jsp_rule24,],
    "Q": [jsp_rule24,],
    "R": [jsp_rule24,],
    "S": [jsp_rule24,],
    "T": [jsp_rule24,],
    "U": [jsp_rule24,],
    "V": [jsp_rule24,],
    "W": [jsp_rule24,],
    "X": [jsp_rule24,],
    "Y": [jsp_rule24,],
    "Z": [jsp_rule24,],
    "a": [jsp_rule24,],
    "b": [jsp_rule24,],
    "c": [jsp_rule24,],
    "d": [jsp_rule24,],
    "e": [jsp_rule24,],
    "f": [jsp_rule24,],
    "g": [jsp_rule24,],
    "h": [jsp_rule24,],
    "i": [jsp_rule24,],
    "j": [jsp_rule24,],
    "k": [jsp_rule24,],
    "l": [jsp_rule24,],
    "m": [jsp_rule24,],
    "n": [jsp_rule24,],
    "o": [jsp_rule24,],
    "p": [jsp_rule24,],
    "q": [jsp_rule24,],
    "r": [jsp_rule24,],
    "s": [jsp_rule24,],
    "t": [jsp_rule24,],
    "u": [jsp_rule24,],
    "v": [jsp_rule24,],
    "w": [jsp_rule24,],
    "x": [jsp_rule24,],
    "y": [jsp_rule24,],
    "z": [jsp_rule24,],
}

# Rules for jsp_tags ruleset.

def jsp_rule25(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="<%--", end="--%>")

def jsp_rule26(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<%=", end="%>",
          delegate="java::main")

def jsp_rule27(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="jsp::attrvalue")

def jsp_rule28(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="jsp::attrvalue")

def jsp_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="/")

def jsp_rule30(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="function", pattern=":",
          exclude_match=True)

def jsp_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

# Rules dict for jsp_tags ruleset.
rulesDict4 = {
    "\"": [jsp_rule27,],
    "'": [jsp_rule28,],
    "/": [jsp_rule29,],
    ":": [jsp_rule30, jsp_rule31,],
    "<": [jsp_rule25, jsp_rule26,],
}

# Rules for jsp_attrvalue ruleset.

def jsp_rule32(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword1", begin="<%=", end="%>",
          delegate="java::main")

# Rules dict for jsp_attrvalue ruleset.
rulesDict5 = {
    "<": [jsp_rule32,],
}

# x.rulesDictDict for jsp mode.
rulesDictDict = {
    "jsp_attrvalue": rulesDict5,
    "jsp_comment": rulesDict2,
    "jsp_directives": rulesDict3,
    "jsp_main": rulesDict1,
    "jsp_tags": rulesDict4,
}

# Import dict for jsp mode.
importDict = {}
