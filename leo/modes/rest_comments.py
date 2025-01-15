#@+leo-ver=5-thin
#@+node:ekr.20250115040652.1: * @file ../modes/rest_comments.py
#@@language python
# Leo colorizer control file for rest_comments mode.
# This file is in the public domain.

import string
from leo.core import leoGlobals as g
assert g

#@+<< rest_comments: properties and attributes >>
#@+node:ekr.20250115040652.2: ** << rest_comments: properties and attributes >>
# Properties for rest_comments mode.
properties = {
    "indentNextLines": ".+::$",
    "lineComment": "..",
}

# Attributes dict for rest_comments mode.
rest_comments_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "false",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for rest_comments mode.
attributesDictDict = {
    "rest_comments_main": rest_comments_main_attributes_dict,
}
#@-<< rest_comments: properties and attributes >>
#@+<< rest_comments: keywords >>
#@+node:ekr.20250115040652.3: ** << rest_comments: keywords >> (empty)
# Dictionary of keywords dictionaries for rest_comments mode.
keywordsDictDict = {
    "rest_comments_main": {}
}
#@-<< rest_comments: keywords >>
#@+<< rest_comments: rules >>
#@+node:ekr.20250115040652.4: ** << rest_comments: rules >>
# Rules for rest_comments_main ruleset.

#@+others
#@+node:ekr.20250115040652.5: *3* rest_comments underline rules
#@+node:ekr.20250115040652.6: *4* function: rest_comments_rule2
def rest_comments_rule2(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="={3,}")
#@+node:ekr.20250115040652.7: *4* function: rest_comments_rule3
def rest_comments_rule3(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="-{3,}")
#@+node:ekr.20250115040652.8: *4* function: rest_comments_rule4
def rest_comments_rule4(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="~{3,}")
#@+node:ekr.20250115040652.9: *4* function: rest_comments_rule5
def rest_comments_rule5(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="`{3,}")
#@+node:ekr.20250115040652.10: *4* function: rest_comments_rule6
def rest_comments_rule6(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="#{3,}")
#@+node:ekr.20250115040652.11: *4* function: rest_comments_rule7
def rest_comments_rule7(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp='"{3,}')
#@+node:ekr.20250115040652.12: *4* function: rest_comments_rule8
def rest_comments_rule8(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\^{3,}")
#@+node:ekr.20250115040652.13: *4* function: rest_comments_rule9
def rest_comments_rule9(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\+{3,}")
#@+node:ekr.20250115040652.14: *3* function: rest_comments_plain_word (literal1)
def rest_comments_plain_word(colorer, s, i):

    j = i
    while j < len(s) and s[j] in string.ascii_letters:
        j += 1
    return colorer.match_seq(s, i, kind='literal1', seq=s[i : j + 1])
#@+node:ekr.20250115040652.15: *3* function: rest_comments_number (literal2)
def rest_comments_number(colorer, s, i):

    j = i
    while j < len(s) and s[j] in string.digits:
        j += 1
    return colorer.match_seq(s, i, kind='literal2', seq=s[i : j + 1])
#@+node:ekr.20250115040652.16: *3* function: rest_comments_default (operator)
def rest_comments_default(colorer, s, i):
    ch = s[i]
    if ch in ' \t':
        return 1
    return colorer.match_seq(s, i, kind='operator', seq=s[i])
#@+node:ekr.20250115040652.17: *3* function: rest_comments_star (comment1, label, literal3, literal4)
def rest_comments_star(colorer, s, i):

    # Count the number of stars in s[i:].
    j = 0
    while i + j < len(s) and s[i + j] == '*':
        j += 1
    seq = '*' * j

    # Case 1: ***
    if j >= 3:
        return colorer.match_seq(s, i, kind="label", seq=seq)

    # Case 2: no matching '*'
    k = s.find(seq, i + j)
    if k == -1:
        return colorer.match_seq(s, i, kind="comment1", seq='*')

    # Case 3: * or **
    # Use keyword2 for italics, keyword3 for bold.
    kind = 'literal3' if len(seq) == 1 else 'literal4'
    return colorer.match_seq(s, i, kind=kind, seq=s[i : k + j])

    # Rule 10.
    # return colorer.match_seq_regexp(s, i, kind="label", regexp="\\*{3,}")
    # Rule 14.
    # return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="\\*\\*[^*]+\\*\\*")
    # Rule 15.
    # return colorer.match_seq_regexp(s, i, kind="keyword4", regexp="\\*[^\\s*][^*]*\\*")
#@+node:ekr.20250115040652.18: *3* function: rest_comments_rule0 __
def rest_comments_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword3", seq="__",
          at_line_start=True)
#@+node:ekr.20250115040652.19: *3* function: rest_comments_rule1 .. _
def rest_comments_rule1(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword3", seq=".. _",
          at_line_start=True)
#@+node:ekr.20250115040652.20: *3* function: rest_comments_rule11 .. |...|
def rest_comments_rule11(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp=r"\.\.\s\|[^|]+\|",
          at_line_start=True)
#@+node:ekr.20250115040652.21: *3* function: rest_comments_rule12 |...|
def rest_comments_rule12(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal4", regexp=r"\|[^|]+\|")
#@+node:ekr.20250115040652.22: *3* function: rest_comments_rule13 .. word::
def rest_comments_rule13(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp=r"\.\.\s[A-z][A-z0-9-_]+::",
          at_line_start=True)
#@+node:ekr.20250115040652.23: *3* function: rest_comments_rule16 ..
def rest_comments_rule16(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="..",
          at_line_start=True)
#@+node:ekr.20250115040652.24: *3* function: rest_comments_rule17 `word`_
def rest_comments_rule17(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="`[A-z0-9]+[^`]+`_{1,2}")
#@+node:ekr.20250115040652.25: *3* function: rest_comments_rule18 [number]_
def rest_comments_rule18(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\[[0-9]+\]_")
#@+node:ekr.20250115040652.26: *3* function: rest_comments_rule19 [#word]_
def rest_comments_rule19(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\[#[A-z0-9_]*\]_")
#@+node:ekr.20250115040652.27: *3* function: rest_comments_rule20 []_
def rest_comments_rule20(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\[*\]_")
#@+node:ekr.20250115040652.28: *3* function: rest_comments_rule21 [word]_
def rest_comments_rule21(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\[[A-z][A-z0-9_-]*\]_")
#@+node:ekr.20250115040652.29: *3* function: rest_comments_rule22 ``...``
def rest_comments_rule22(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="``", end="``")
#@+node:ekr.20250115040652.30: *3* function: rest_comments_rule23 `...`
def rest_comments_rule23(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp="`[^`]+`")
#@+node:ekr.20250115040652.31: *3* function: rest_comments_rule24 :word=:
def rest_comments_rule24(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword1", regexp=r":[A-z][A-z0-9 \t=\s\t_]*:")
#@+node:ekr.20250115040652.32: *3* function: rest_comments_rule25 +-
def rest_comments_rule25(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\+-[+-]+")
#@+node:ekr.20250115040652.33: *3* function: rest_comments_rule26 +=
def rest_comments_rule26(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp=r"\+=[+=]+")
#@-others
#@-<< rest_comments: rules >>
#@+<< rest_comments: rulesDict1 >>
#@+node:ekr.20250115040652.34: ** << rest_comments: rulesDict1 >>
# Rules dict for rest_comments_main ruleset.
rulesDict1 = {
    "\"": [rest_comments_rule7],
    "#": [rest_comments_rule6],
    "*": [rest_comments_star],
    "+": [rest_comments_rule9, rest_comments_rule25, rest_comments_rule26],
    "-": [rest_comments_rule3],
    ".": [
            rest_comments_rule1,
            rest_comments_rule11,
            rest_comments_rule13,
            rest_comments_rule16,
        ],
    ":": [rest_comments_rule24],
    "=": [rest_comments_rule2],
    "[": [
            rest_comments_rule18,
            rest_comments_rule19,
            rest_comments_rule20,
            rest_comments_rule21,
        ],
    "^": [rest_comments_rule8],
    "_": [rest_comments_rule0],
    "`": [
            rest_comments_rule5,
            rest_comments_rule17,
            rest_comments_rule22,
            rest_comments_rule23,
        ],
    "|": [rest_comments_rule12],
    "~": [rest_comments_rule4],
}

# Color words and numbers explicitly, allowing them to have non-default colors.

lead_in_table = (
    (string.ascii_letters, rest_comments_plain_word),
    (string.digits, rest_comments_number),
)
for lead_ins, matcher in lead_in_table:
    for lead_in in lead_ins:
        aList = rulesDict1.get(lead_in, [])
        if matcher not in aList:
            aList.insert(0, matcher)
            rulesDict1[lead_in] = aList

# Color everything as literal1 by default.
for lead_in in string.printable:
    aList = rulesDict1.get(lead_in, [])
    aList.append(rest_comments_default)
    rulesDict1[lead_in] = aList

#@-<< rest_comments: rulesDict1 >>

# x.rulesDictDict for rest_comments mode.
rulesDictDict = {
    "rest_comments_main": rulesDict1,
}

# Import dict for rest_comments mode.
importDict = {}
#@-leo
