#@+leo-ver=5-thin
#@+node:ekr.20250121105007.1: * @file ../modes/cweb.py
# Leo colorizer control file for cweb mode.
# This file is in the public domain.

import string

in_doc_part = False  # True: in @doc part. It continues until any @x directive.

#@+others
#@-others

#@+<< cweb: properties >>
#@+node:ekr.20250123062334.1: ** << cweb: properties >>

# Properties for cweb mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "doubleBracketIndent": "false",
    "indentCloseBrackets": "}",
    "indentNextLine": "\\s*(((if|while)\\s*\\(|else\\s*|else\\s+if\\s*\\(|for\\s*\\(.*\\))[^{;]*)",
    "indentOpenBrackets": "{",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
    "wordBreakChars": ",+-=<>/?^&*",
}
#@-<< cweb: properties >>
#@+<< cweb: attributes & dict >>
#@+node:ekr.20250123062356.1: ** << cweb: attributes & dict >>

# Attributes dict for cweb_main ruleset.
cweb_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for cweb_cpp ruleset.
# cweb_cpp_attributes_dict = {
    # "default": "KEYWORD2",
    # "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    # "escape": "\\",
    # "highlight_digits": "true",
    # "ignore_case": "false",
    # "no_word_sep": "",
# }

# Attributes dict for cweb_include ruleset.
# cweb_include_attributes_dict = {
    # "default": "KEYWORD2",
    # "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    # "escape": "\\",
    # "highlight_digits": "true",
    # "ignore_case": "false",
    # "no_word_sep": "",
# }

# Dictionary of attributes dictionaries for cweb mode.
attributesDictDict = {
    # "cweb_cpp": cweb_cpp_attributes_dict,
    # "cweb_include": cweb_include_attributes_dict,
    "cweb_main": cweb_main_attributes_dict,
}
#@-<< cweb: attributes & dict >>
#@+<< cweb: keywords dict >>
#@+node:ekr.20250123062431.1: ** << cweb: keywords dict >>

# Keywords dict for cweb_main ruleset.
cweb_main_keywords_dict = {
    "NULL": "literal2",
    "asm": "keyword2",
    "asmlinkage": "keyword2",
    "auto": "keyword1",
    "break": "keyword1",
    "case": "keyword1",
    "char": "keyword3",
    "const": "keyword1",
    "continue": "keyword1",
    "default": "keyword1",
    "do": "keyword1",
    "double": "keyword3",
    "else": "keyword1",
    "enum": "keyword3",
    "extern": "keyword1",
    "false": "literal2",
    "far": "keyword2",
    "float": "keyword3",
    "for": "keyword1",
    "goto": "keyword1",
    "huge": "keyword2",
    "if": "keyword1",
    "inline": "keyword2",
    "int": "keyword3",
    "long": "keyword3",
    "near": "keyword2",
    "pascal": "keyword2",
    "register": "keyword1",
    "return": "keyword1",
    "short": "keyword3",
    "signed": "keyword3",
    "sizeof": "keyword1",
    "static": "keyword1",
    "struct": "keyword3",
    "switch": "keyword1",
    "true": "literal2",
    "typedef": "keyword3",
    "union": "keyword3",
    "unsigned": "keyword3",
    "void": "keyword3",
    "volatile": "keyword1",
    "while": "keyword1",
}

# Dictionary of keywords dictionaries for cweb mode.
keywordsDictDict = {
    # "cweb_cpp": cweb_cpp_keywords_dict,
    # "cweb_include": cweb_include_keywords_dict,
    "cweb_main": cweb_main_keywords_dict,
}
#@-<< cweb: keywords dict >>
#@+<< cweb: rules >>
#@+node:ekr.20250123062533.1: ** << cweb: rules >>
# Rules for cweb_main ruleset.

#@+others
#@+node:ekr.20250123061808.1: *3* function: cweb_rule0 /**
def cweb_rule0(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="doxygen::doxygen")
#@+node:ekr.20250123061808.2: *3* function: cweb_rule1 /*!
def cweb_rule1(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_span(s, i, kind="comment3", begin="/*!", end="*/",
          delegate="doxygen::doxygen")
#@+node:ekr.20250123061808.3: *3* function: cweb_rule2 /*
def cweb_rule2(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")
#@+node:ekr.20250123061808.4: *3* function: cweb_rule3 "
def cweb_rule3(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)
#@+node:ekr.20250123061808.5: *3* function: cweb_rule4 '
def cweb_rule4(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)
#@+node:ekr.20250123061808.6: *3* function: cweb_rule5 ##
def cweb_rule5(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="##")
#@+node:ekr.20250123061808.7: *3* function: cweb_rule6 #
def cweb_rule6(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    # #4283: Colorize the whole line.
    return colorer.match_eol_span(s, i, kind="keyword2")
#@+node:ekr.20250123061808.8: *3* function: cweb_rule7 // comment
def cweb_rule7(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")
#@+node:ekr.20250123070417.1: *3* rules: operators
def cweb_rule8(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def cweb_rule9(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def cweb_rule10(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def cweb_rule11(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def cweb_rule12(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def cweb_rule13(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def cweb_rule14(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def cweb_rule15(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def cweb_rule16(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def cweb_rule17(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def cweb_rule18(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def cweb_rule19(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def cweb_rule20(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def cweb_rule21(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def cweb_rule22(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def cweb_rule23(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def cweb_rule24(colorer, s, i):
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def cweb_rule_semicolon(colorer, s, i):  # #4283.
    global in_doc_part
    if in_doc_part:
        return 0
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

#@+node:ekr.20250302054554.1: *3* function: cweb_rule_at_sign
def cweb_rule_at_sign(colorer, s, i):
    """
    Handle cweb directives. @ continues until the next directive.
    """
    global in_doc_part

    seq = s[i : i + 2]
    if i == 0 and s[i] == '@':
        old_in_doc_part = in_doc_part
        in_doc_part = seq in ('@', '@ ', '@*')
        if old_in_doc_part:
            return colorer.match_seq(s, i, kind="keyword1", seq=seq)
        elif in_doc_part:
                return colorer.match_seq(s, i, kind="keyword1", seq=seq)

    if seq in ('@<', '@.'):
        # Color sections.
        j = s.find('@>', i + 2)
        if j > -1:
            colorer.match_seq(s, i, kind="keyword1", seq=seq)
            seq2 = s[i + 2 : j]
            colorer.match_seq(s, i + 2, kind="label", seq=seq2)
            colorer.match_line(s, j, kind="keyword1")
            return 0
        return colorer.match_line(s, i, kind="keyword1")
    return colorer.match_seq(s, i, kind="keyword1", seq=seq)
#@+node:ekr.20250123061808.27: *3* function: cweb_rule26 (
def cweb_rule26(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)
#@+node:ekr.20250123061808.28: *3* function: cweb_keyword & label
def cweb_keyword(colorer, s, i):
    global in_doc_part

    if in_doc_part:
        return 0

    # cweb_rule_at_sign handles all section references.
    seq = s[i : i + 2]
    if seq in ('@<', '@.'):
        return 0
    return  colorer.match_keywords(s, i)

#@+node:ekr.20250302073158.1: *3* function: cweb_backslash
def cweb_backslash(colorer, s, i):
    """Handle TeX control sequences."""
    i1 = i
    print('bs', s)
    # Non-alphabetic.
    seq = s[i : i + 2]
    if seq == '\\' or len(seq) > 1 and not seq[1].isalpha():
        return colorer.match_seq(s, i1, kind="keyword1", seq=seq)
    # Alphabetic
    i += 2
    while i <len(s) and s[i].isalpha():
        i += 1
    seq = s[i1: i]
    return colorer.match_seq(s, i1, kind="keyword1", seq=seq)
#@-others
#@-<< cweb: rules >>
#@+<< cweb: rules dict >>
#@+node:ekr.20250123062712.1: ** << cweb: rules dict >>
# Rules dict for cweb_main ruleset.
rulesDict1 = {
    ";": [cweb_rule_semicolon],  # #4283.
    "@": [cweb_rule_at_sign],
    "!": [cweb_rule9],
    '"': [cweb_rule3],
    "#": [cweb_rule5, cweb_rule6],
    "%": [cweb_rule18],
    "&": [cweb_rule19],
    "'": [cweb_rule4],
    "(": [cweb_rule26],
    "*": [cweb_rule15],
    "+": [cweb_rule12],
    "-": [cweb_rule13],
    "/": [cweb_rule0, cweb_rule1, cweb_rule2, cweb_rule7, cweb_rule14],
    "<": [cweb_rule11, cweb_rule17],
    "=": [cweb_rule8],
    ">": [cweb_rule10, cweb_rule16],
    "^": [cweb_rule21],
    "{": [cweb_rule24],
    "|": [cweb_rule20],
    "}": [cweb_rule23],
    "~": [cweb_rule22],
    "\\": [cweb_backslash],
}

# Add *all* characters that could start a cweb identifier.
lead_ins = string.ascii_letters + '_'
for lead_in in lead_ins:
    aList = rulesDict1.get(lead_in, [])
    if cweb_keyword not in aList:
        aList.insert(0, cweb_keyword)
        rulesDict1[lead_in] = aList
#@-<< cweb: rules dict >>

# x.rulesDictDict for cweb mode.
rulesDictDict = {
    "cweb_main": rulesDict1,
}

# Import dict for cweb mode.
importDict = {}

#@@language python
#@@tabwidth -4
#@-leo
