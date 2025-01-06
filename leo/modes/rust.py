#@+leo-ver=5-thin
#@+node:ekr.20231103124615.1: * @file ../modes/rust.py
# Leo colorizer control file for rust mode.
# This file is in the public domain.

import re
from leo.core import leoGlobals as g

#@+<< Rust properties dict >>
#@+node:ekr.20250106042726.1: ** << Rust properties dict >>
# Properties for rust mode.
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
#@-<< Rust properties dict >>
#@+<< Rust attributes dicts >>
#@+node:ekr.20250105164117.1: ** << Rust attributes dicts >>
# Attributes dict for rust_main ruleset.
rust_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]_]+[lL]?|[[:digit:]_]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for rust mode.
attributesDictDict = {
    "rust_main": rust_main_attributes_dict,
}
#@-<< Rust attributes dicts >>
#@+<< Rust keywords dicts >>
#@+node:ekr.20250106043953.1: ** << Rust keywords dicts >>
# Keywords dict for rust_main ruleset.
rust_main_keywords_dict = {
    'Self': 'keyword1',
    'abstract': 'keyword1',
    'as': 'keyword1',
    'async': 'keyword1',
    'become': 'keyword1',
    'bool': 'keyword2',
    'box': 'keyword1',
    'break': 'keyword1',
    'const': 'keyword1',
    'continue': 'keyword1',
    'crate': 'keyword1',
    'do': 'keyword1',
    'dyn': 'keyword1',
    'else': 'keyword1',
    'enum': 'keyword1',
    'extern': 'keyword1',
    'false': 'keyword1',
    'final': 'keyword1',
    'fn': 'keyword1',
    'for': 'keyword1',
    'i16': 'keyword2',
    'i32': 'keyword2',
    'i64': 'keyword2',
    'i8': 'keyword2',
    'if': 'keyword1',
    'impl': 'keyword1',
    'in': 'keyword1',
    'let': 'keyword1',
    'loop': 'keyword1',
    'macro': 'keyword1',
    'match': 'keyword1',
    'mod': 'keyword1',
    'move': 'keyword1',
    'mut': 'keyword1',
    'override': 'keyword1',
    'priv': 'keyword1',
    'pub': 'keyword1',
    'ref': 'keyword1',
    'return': 'keyword1',
    'self': 'keyword1',
    'static': 'keyword1',
    'str': 'keyword2',
    'struct': 'keyword1',
    'super': 'keyword1',
    'trait': 'keyword1',
    'true': 'keyword1',
    'try': 'keyword1',
    'type': 'keyword1',
    'typeof': 'keyword1',
    'u16': 'keyword2',
    'u32': 'keyword2',
    'u64': 'keyword2',
    'u8': 'keyword2',
    'unsafe': 'keyword1',
    'unsized': 'keyword1',
    'use': 'keyword1',
    'usize': 'keyword2',
    'vec!': 'keyword2',
    'virtual': 'keyword1',
    'where': 'keyword1',
    'while': 'keyword1',
    'yield': 'keyword1',
    'Some': 'keyword3',
    'None': 'keyword3',
    'Result': 'keyword3',
    'Err': 'keyword3',
    'Ok': 'keyword3',
    'include_bytes': 'keyword2',
    'include_str': 'keyword2',
}

# Dictionary of keywords dictionaries for rust mode.
keywordsDictDict = {
    "rust_main": rust_main_keywords_dict,
}
#@-<< Rust keywords dicts >>
#@+<< Rust rules >>
#@+node:ekr.20250105163810.1: ** << Rust rules >>
# Rules for rust_main ruleset.
#@+others
#@+node:ekr.20250106042808.3: *3* function: rust_rule2
def rust_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")
#@+node:ekr.20250106054207.1: *3* function: rust_slash (comments & operators)
def rust_slash(colorer, s, i):

    # match_span constructs.
    match_span_table = (
        ('/**', 'comment3', 'doxygen'),
        ('/*!', 'comment3', 'doxygen'),
        ('/*', 'comment1', None),
    )
    for begin, kind, delegate in match_span_table:
        if i + len(begin) < len(s) and s[i : i + len(begin)] == begin:
            return colorer.match_span(s, i,
                kind=kind, begin=begin, end="*/", delegate=delegate)

    # match_seq constructs.
    match_seq_table = (
        ('//', 'comment2', colorer.match_eol_span),
        ('/', 'operator', colorer.match_plain_seq),
    )
    for seq, kind, matcher in match_seq_table:
        if i + len(seq) < len(s) and s[i : i + len(seq)] == seq:
            return matcher(s, i, kind=kind, seq=seq)

    # Fail.
    return i + 1
#@+node:ekr.20250106062326.1: *3* rust: strings and chars, with escapes
#@+node:ekr.20250106062904.1: *4* function: get_escaped_char
# '\u{7FFF}'
char10_pat = re.compile(r"'\\u\{[0-7][0-7a-fA-F]{3}\}'")
# '\x7F'
char6_pat = re.compile(r"'\\x[0-7][0-7a-fA-F]'")
# '\n', '\r', '\t', '\\', '\0', '\'', '\"'
char4_pat = re.compile(r"'\\[\\\"'nrt0]'")
# 'x' where x is any unicode character.
char3_pat = re.compile(r"'.'", re.UNICODE)

def get_escaped_char(s, i):
    """
    This is a helper, not a matcher.
    
    Return the entire escaped character.
    """
    for pat in char10_pat, char6_pat, char4_pat, char3_pat:
        m = pat.match(s, i)
        if m:
            return m.group(0)
    return i + 2  # User error?
#@+node:ekr.20250106042808.5: *4* function: rust_char
# A single quote does not always denote a character literal.

# These patterns are the same as in the rust importer:
def rust_char(colorer, s, i):
    ### assert s[i] == "'"
    g.trace(s[i:])  ###
    if i + 1 >= len(s):
        return len(s)
    if i + 1 == '\\':
        seq = get_escaped_char(s, i)
    else:
        seq = s[i : i + 2]
    return colorer.match_seq(s, i, kind="literal2", seq=s[i : i + 2])

# def rust_char10(colorer, s, i):
    # return colorer.match_span_regexp(s, i, kind="literal2", begin=char10_pat)
# def rust_char6(colorer, s, i):
    # return colorer.match_span_regexp(s, i, kind="literal2", begin=char6_pat)
# def rust_char4(colorer, s, i):
    # return colorer.match_span_regexp(s, i, kind="literal2", begin=char4_pat)
# def rust_char3(colorer, s, i):
    # return colorer.match_span_regexp(s, i, kind="literal2", begin=char3_pat)
#@+node:ekr.20250106052237.1: *4* function: rust_string (to do: char escapes)
def rust_string(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="\"", end="\"")
#@+node:ekr.20250106042808.9: *3* function: rust_raw_string_literal
# #3631
# https://doc.rust-lang.org/reference/tokens.html#raw-string-literals
# Up to 255 '#' are allowed. Ruff only uses 1 and 3.

def rust_raw_string_literal(colorer, s, i):
    if i + 1 >= len(s):
        return len(s)
    if s[i + 1] != '#':
        return i + 1
    for n in (3, 2, 1):
        begin = 'r' + '#' * n
        end = '#' * n
        if g.match(s, i, begin):
            return colorer.match_span(s, i, kind="literal2", begin=begin, end=end)
    return i + 1

# def rust_raw_string_literal3(colorer, s, i):
    # return colorer.match_span(s, i, kind="literal2", begin='r###"', end='"###')
# def rust_raw_string_literal2(colorer, s, i):
    # return colorer.match_span(s, i, kind="literal2", begin='r##"', end='"##')
# def rust_raw_string_literal1(colorer, s, i):
    # return colorer.match_span(s, i, kind="literal2", begin='r#"', end='"#')
#@+node:ekr.20250106042808.12: *3* function: rust_at_operator
def rust_at_operator(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")
#@+node:ekr.20250106054547.1: *3* function: rust_pound
def rust_pound(colorer, s, i):
    return 0  ###

# def rust_rule5(colorer, s, i):
    # return colorer.match_plain_seq(s, i, kind="keyword2", seq="##")
# def rust_rule6(colorer, s, i):
    # return colorer.match_eol_span(s, i, kind="keyword2", seq="#")
#@+node:ekr.20250106054731.1: *3* function: rust_open_angle & rust_close_angle
def rust_open_angle(colorer, s, i):
    if s[i] != '<':  # May fail during unit tests!
        return 0
    seq = '<=' if i + i < len(s) and s[i + 1] == '=' else '<'
    return colorer.match_plain_seq(s, i, kind="operator", seq=seq)

def rust_close_angle(colorer, s, i):
    if s[i] != '>':
        return 0
    seq = '>=' if i + i < len(s) and s[i + 1] == '=' else '>'
    return colorer.match_plain_seq(s, i, kind="operator", seq=seq)
#@+node:ekr.20250106042808.14: *3* function: rust_rule6
def rust_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#")
#@+node:ekr.20250106042808.16: *3* function: rust_rule8
def rust_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")
#@+node:ekr.20250106042808.17: *3* function: rust_rule9
def rust_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")
#@+node:ekr.20250106042808.20: *3* function: rust_rule12
def rust_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")
#@+node:ekr.20250106042808.21: *3* function: rust_rule13
def rust_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")
#@+node:ekr.20250106042808.23: *3* function: rust_rule15
def rust_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")
#@+node:ekr.20250106042808.24: *3* function: rust_rule16
def rust_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")
#@+node:ekr.20250106042808.25: *3* function: rust_rule17
def rust_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")
#@+node:ekr.20250106042808.26: *3* function: rust_rule18
def rust_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")
#@+node:ekr.20250106042808.27: *3* function: rust_rule19
def rust_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")
#@+node:ekr.20250106042808.28: *3* function: rust_rule20
def rust_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")
#@+node:ekr.20250106042808.29: *3* function: rust_rule21
def rust_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")
#@+node:ekr.20250106042808.30: *3* function: rust_rule22
def rust_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")
#@+node:ekr.20250106042808.31: *3* function: rust_rule23
def rust_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")
#@+node:ekr.20250106042808.32: *3* function: rust_rule24
def rust_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")
#@+node:ekr.20250106042808.33: *3* function: rust_rule25
def rust_rule25(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)
#@+node:ekr.20250106042808.34: *3* function: rust_rule26
def rust_rule26(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)
#@+node:ekr.20250106042808.35: *3* function: rust_keywords
def rust_keywords(colorer, s, i):
    return colorer.match_keywords(s, i)
#@-others
#@-<< Rust rules >>
#@+<< Rust rules dicts >>
#@+node:ekr.20231103125350.1: ** << Rust rules dicts >>
# Rules dict for rust.
rulesDict1 = {
    "!": [rust_rule9],
    "#": [rust_pound],
    "/": [rust_slash],
    "r": [rust_raw_string_literal],  # New.
    '"': [rust_string],  # New.
    "'": [rust_char],  # New.
    "<": [rust_open_angle],  # New.
    ">": [rust_close_angle],  # New.
    "&": [rust_rule19],
    "%": [rust_rule18],
    "(": [rust_rule26],
    "*": [rust_rule15],
    "+": [rust_rule12],
    "-": [rust_rule13],
    ":": [rust_rule25],
    "=": [rust_rule8],
    "@": [rust_at_operator],
    "^": [rust_rule21],
    "{": [rust_rule24],
    "|": [rust_rule20],
    "}": [rust_rule23],
    "~": [rust_rule22],
}

# Prepend entries for rust_keyword to rulesDict1.
lead_ins = list(sorted(set(key[0] for key in rust_main_keywords_dict)))
# print('rust lead-ins', lead_ins)
for lead_in in lead_ins:
    aList = rulesDict1.get(lead_in, [])
    aList.insert(0, rust_keywords)
    rulesDict1[lead_in] = aList

# g.printObj(rulesDict1, tag='rulesDict1')

# x.rulesDictDict for rust mode.
rulesDictDict = {
    "rust_main": rulesDict1,
}
#@-<< Rust rules dicts >>

# Import dict for rust mode.
importDict = {}
#@-leo
