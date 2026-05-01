# @+leo-ver=5-thin
# @+node:swot.20260501212006.1: * @file /Users/swot/app/leo-editor/leo/modes/pug.py
# @@language python
# @+<< docs >>
# @+node:swot.20260501212107.1: ** << docs >>
# @+doc
# leo/modes/pug.py: Leo's mode file for @language pug.
#
# Supports:
#
# - Comments: //- (non-output), // (output)
# - Tag names (div, p, a, etc.)
# - CSS selectors (#id, .class)
# - HTML attributes with double/single quoted strings
# - Backslash line continuation in double-quoted strings: "foo \\n  bar \\n  baz"
# - Interpolation: #{}, !{}
# - Pug directives: doctype, if/else/each/mixin/include/block/extends/case/when/default/append/prepend
# - Embedded script: and style: blocks delegating to javascript/css
# - Keywords: true/false/and/or/not/null/undefined
#
#
# Design notes on cross-line strings:
#
#   leo's match_span uses a 'dots' hack for continued strings which
#   suppresses setRestart.  This means lines after a backslash-\n
#   lose all colouring until the closing quote.  We therefore use a
#   custom matcher for "..." that calls setRestart explicitly.
# @-<< docs >>
# @+<< import >>
# @+node:swot.20260501213739.1: ** << import >>
from __future__ import annotations
import re
import string
from typing import Any
from leo.core import leoGlobals as g

assert g
# @-<< import >>
# @+others
# @+node:swot.20260501214155.1: ** pug_rule
# @+node:swot.20260501212231.1: *3* pug_rule_comment_buf
def pug_rule_comment_buf(colorer: Any, s: str, i: int) -> int:
    """Match buffer-only (non-output) Pug comment: //-"""
    return colorer.match_eol_span(s, i, kind="comment1", seq="//-")
# @+node:swot.20260501212428.1: *3* pug_rule_comment
def pug_rule_comment(colorer: Any, s: str, i: int) -> int:
    """Match output Pug comment: //"""
    # Must not match //- (handled by pug_rule_comment_buf first).
    return colorer.match_eol_span(s, i, kind="comment1", seq="//")
# @+node:swot.20260501212453.1: *3* pug_rule_handlebar
def pug_rule_handlebar(colorer: Any, s: str, i: int) -> int:
    """Match Vue/Pug handlebar expression: {{...}}"""
    return colorer.match_span(s, i, kind="keyword3", begin="{{", end="}}")
# @+node:swot.20260501212551.1: *3* pug_rule_interpolation
def pug_rule_interpolation(colorer: Any, s: str, i: int) -> int:
    """Match Pug interpolation: #{...} or !{...}"""
    n = colorer.match_span(s, i, kind="literal3", begin="#{", end="}")
    if n:
        return n
    return colorer.match_span(s, i, kind="literal3", begin="!{", end="}")
# @+node:swot.20260501212628.1: *3* pug_rule_component
def pug_rule_component(colorer: Any, s: str, i: int) -> int:
    """Match Vue/Pug custom component names (PascalCase, no colouring)."""
    if i >= len(s) or not s[i].isupper():
        return 0
    j = i + 1
    while j < len(s) and (s[j].isalnum() or s[j] in '_-'):
        j += 1
    if j > i:
        return j - i
    return 0
# @+node:swot.20260501212654.1: *3* pug_rule_vue_directive
def pug_rule_vue_directive(colorer: Any, s: str, i: int) -> int:
    """Match Vue directives: v-if, v-else, v-for, v-model, etc."""
    if not s.startswith("v-", i):
        return 0
    j = i + 2
    while j < len(s) and (s[j].isalnum() or s[j] == "-"):
        j += 1
    if j > i + 2:
        colorer.colorRangeWithTag(s, i, j, tag="keyword1")
        return j - i
    return 0
# @+node:swot.20260501212707.1: *3* pug_rule_vue_bind
def pug_rule_vue_bind(colorer: Any, s: str, i: int) -> int:
    """Match Vue bind shorthand: :class, :src, etc."""
    if s[i] != ":":
        return 0
    j = i + 1
    while j < len(s) and (s[j].isalnum() or s[j] in "-_."):
        j += 1
    if j > i + 1:
        colorer.colorRangeWithTag(s, i, j, tag="keyword1")
        return j - i
    return 0
# @+node:swot.20260501212723.1: *3* pug_rule_vue_event
def pug_rule_vue_event(colorer: Any, s: str, i: int) -> int:
    """Match Vue event shorthand: @click, @submit, etc."""
    if s[i] != "@":
        return 0
    j = i + 1
    while j < len(s) and (s[j].isalnum() or s[j] in "-_."):
        j += 1
    if j > i + 1:
        colorer.colorRangeWithTag(s, i, j, tag="keyword1")
        return j - i
    return 0
# @+node:swot.20260501212738.1: *3* pug_rule_attribute
def pug_rule_attribute(colorer: Any, s: str, i: int) -> int:
    """Match HTML attribute names inside attribute lists."""
    if not s[i].isalpha():
        return 0
    j = i + 1
    while j < len(s) and (s[j].isalnum() or s[j] in "-_"):
        j += 1
    # Must be followed by optional whitespace then = or (
    k = j
    while k < len(s) and s[k] in " \t":
        k += 1
    if k < len(s) and s[k] in "=(:":
        # Only match if preceded by ( or , (inside attribute list)
        prev = ""
        for p in range(i - 1, -1, -1):
            if s[p] not in " \t":
                prev = s[p]
                break
        if prev in "(,:":
            colorer.colorRangeWithTag(s, i, j, tag="keyword1")
            return j - i
    return 0
# @+node:swot.20260501212806.1: *3* pug_rule_keyword
def pug_rule_keyword(colorer: Any, s: str, i: int) -> int:
    """Match keywords from keywordsDict (HTML tags, Pug directives, etc.)."""
    return colorer.match_keywords(s, i)
# @+node:swot.20260501212819.1: *3* pug_rule_css_id
def pug_rule_css_id(colorer: Any, s: str, i: int) -> int:
    """Match CSS id selector: #id (no colouring – default white)."""
    if i > 0 and s[i - 1] not in (' ', '\t', '\n', '('):
        return 0
    m = re.match(r'#[a-zA-Z_][a-zA-Z0-9_-]*', s[i:])
    if m:
        return m.end()
    return 0
# @+node:swot.20260501213001.1: *3* pug_rule_css_class
def pug_rule_css_class(colorer: Any, s: str, i: int) -> int:
    """Match CSS class selector: .class (no colouring – default white)."""
    if i > 0 and s[i - 1] not in (' ', '\t', '\n', '('):
        return 0
    m = re.match(r'\.[a-zA-Z_][a-zA-Z0-9_-]*', s[i:])
    if m:
        return m.end()
    return 0
# @+node:swot.20260501213014.1: *3* pug_rule_paren_open
def pug_rule_paren_open(colorer: Any, s: str, i: int) -> int:
    """Match opening parenthesis: ( (no colouring)."""
    if i < len(s) and s[i] == "(":
        return 1
    return 0
# @+node:swot.20260501213024.1: *3* pug_rule_paren_close
def pug_rule_paren_close(colorer: Any, s: str, i: int) -> int:
    """Match closing parenthesis: ) (no colouring)."""
    if i < len(s) and s[i] == ")":
        return 1
    return 0
# @+node:swot.20260501213038.1: *3* pug_rule_dq_string
def pug_rule_dq_string(colorer: Any, s: str, i: int) -> int:
    """Match double-quoted string with backslash line continuation.

    We do NOT use match_span because leo's 'dots' optimisation
    suppresses setRestart for continued literal strings, causing
    all subsequent lines to lose colouring until the closing quote.
    """
    if i >= len(s) or s[i] != '"':
        return 0

    j = i + 1
    while j < len(s):
        if s[j] == '\\' and j + 1 < len(s):
            j += 2
        elif s[j] == '"':
            colorer.colorRangeWithTag(s, i, j + 1, tag="literal1")
            return j + 1 - i
        else:
            j += 1

    # No closing quote on this line – string continues.
    colorer.colorRangeWithTag(s, i, len(s), tag="literal1")

    def restart_dq_string(s: str) -> int:
        k = 0
        while k < len(s):
            if s[k] == '\\' and k + 1 < len(s):
                k += 2
            elif s[k] == '"':
                colorer.colorRangeWithTag(s, 0, k + 1, tag="literal1")
                colorer.clearState()  # End restart – restore normal colouring.
                return k + 1
            else:
                k += 1
        # Still continuing past this line – re-arm the restart.
        colorer.colorRangeWithTag(s, 0, len(s), tag="literal1")
        colorer.setRestart(restart_dq_string)
        return len(s) + 1

    colorer.setRestart(restart_dq_string)
    return len(s) - i
# @+node:swot.20260501213057.1: *3* pug_rule_sq_string
def pug_rule_sq_string(colorer: Any, s: str, i: int) -> int:
    """Match single-quoted string with backslash line continuation."""
    if i >= len(s) or s[i] != "'":
        return 0

    j = i + 1
    while j < len(s):
        if s[j] == '\\' and j + 1 < len(s):
            j += 2
        elif s[j] == "'":
            colorer.colorRangeWithTag(s, i, j + 1, tag="literal1")
            return j + 1 - i
        else:
            j += 1

    # No closing quote on this line – string continues.
    colorer.colorRangeWithTag(s, i, len(s), tag="literal1")

    def restart_sq_string(s: str) -> int:
        k = 0
        while k < len(s):
            if s[k] == '\\' and k + 1 < len(s):
                k += 2
            elif s[k] == "'":
                colorer.colorRangeWithTag(s, 0, k + 1, tag="literal1")
                colorer.clearState()  # End restart – restore normal colouring.
                return k + 1
            else:
                k += 1
        # Still continuing past this line – re-arm the restart.
        colorer.colorRangeWithTag(s, 0, len(s), tag="literal1")
        colorer.setRestart(restart_sq_string)
        return len(s) + 1

    colorer.setRestart(restart_sq_string)
    return len(s) - i
# @+node:swot.20260501213117.1: *3* pug_rule_equals
def pug_rule_equals(colorer: Any, s: str, i: int) -> int:
    """Match = operator in attribute."""
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")
# @+node:swot.20260501213126.1: *3* pug_rule_comma
def pug_rule_comma(colorer: Any, s: str, i: int) -> int:
    """Match comma separator in attributes."""
    return colorer.match_seq(s, i, kind="operator", seq=",")
# @+node:swot.20260501213136.1: *3* pug_rule_script_block
def pug_rule_script_block(colorer: Any, s: str, i: int) -> int:
    """
    Match script: block at start of line.
    Colorizes the 'script:' prefix, then delegates to javascript.
    """
    if i == 0 and s.startswith("script:"):
        colorer.colorRangeWithTag(s, i, i + 7, kind="markup")
        colorer.push_delegate('javascript')
        return len(s)
    return 0
# @+node:swot.20260501213146.1: *3* pug_rule_style_block
def pug_rule_style_block(colorer: Any, s: str, i: int) -> int:
    """
    Match style: block at start of line.
    Colorizes the 'style:' prefix, then delegates to css.
    """
    if i == 0 and s.startswith("style:"):
        colorer.colorRangeWithTag(s, i, i + 6, kind="markup")
        colorer.push_delegate('css')
        return len(s)
    return 0
# @+node:swot.20260501213204.1: *3* pug_rule_doctype
def pug_rule_doctype(colorer: Any, s: str, i: int) -> int:
    """Match doctype declaration."""
    if i == 0 and s.startswith("doctype"):
        colorer.match_seq(s, i, kind="keyword1", seq="doctype")
        return len(s)
    return 0
# @+node:swot.20260501213221.1: *3* pug_rule_pipe
def pug_rule_pipe(colorer: Any, s: str, i: int) -> int:
    """Match pipe character | for raw text."""
    if i == 0 and s.startswith("|"):
        colorer.match_seq(s, i, kind="operator", seq="|")
        return len(s)
    return 0
# @+node:swot.20260501213659.1: ** dicts

# @+node:swot.20260501214636.1: *3* properties
properties = {
    "commentEnd": "",
    "commentStart": "//-",
}
# @+node:swot.20260501214617.1: *3* attributesDictDict
pug_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "-",
}

attributesDictDict = {
    "pug_main": pug_main_attributes_dict,
}
# @+node:swot.20260501214553.1: *3* keywordsDictDict
pug_main_keywords_dict = {
    # Pug directives - colored as keyword1
    "doctype": "keyword1",
    "if": "keyword1",
    "else": "keyword1",
    "else if": "keyword1",
    "unless": "keyword1",
    "each": "keyword1",
    "for": "keyword1",
    "while": "keyword1",
    "in": "keyword1",
    "case": "keyword1",
    "when": "keyword1",
    "default": "keyword1",
    "mixin": "keyword1",
    "include": "keyword1",
    "extends": "keyword1",
    "block": "keyword1",
    "append": "keyword1",
    "prepend": "keyword1",
    "yield": "keyword1",
    # Pug keywords
    "true": "keyword1",
    "false": "keyword1",
    "null": "keyword1",
    "undefined": "keyword1",
    "and": "keyword1",
    "or": "keyword1",
    "not": "keyword1",
    # Vue directives - colored as keyword1 (logic control)
    "v-if": "keyword1",
    "v-else": "keyword1",
    "v-else-if": "keyword1",
    "v-for": "keyword1",
    "v-show": "keyword1",
    "v-model": "keyword1",
    "v-bind": "keyword1",
    "v-on": "keyword1",
    "v-text": "keyword1",
    "v-html": "keyword1",
    "v-slot": "keyword1",
    "v-pre": "keyword1",
    "v-cloak": "keyword1",
    "v-once": "keyword1",
    # HTML common attributes - colored as keyword1 (orange)
    "class": "keyword1",
    "id": "keyword1",
    "src": "keyword1",
    "alt": "keyword1",
    "href": "keyword1",
    "title": "keyword1",
    "type": "keyword1",
    "name": "keyword1",
    "value": "keyword1",
    "placeholder": "keyword1",
    "disabled": "keyword1",
    "readonly": "keyword1",
    "required": "keyword1",
    "checked": "keyword1",
    "selected": "keyword1",
    "target": "keyword1",
    "rel": "keyword1",
    "role": "keyword1",
    "tabindex": "keyword1",
}

keywordsDictDict = {
    "pug_main": pug_main_keywords_dict,
}
# @+node:swot.20260501214353.1: *3* rulesDict1
rulesDict1 = {
    "/": [
        pug_rule_comment_buf,
        pug_rule_comment,
    ],
    "\"": [pug_rule_dq_string],
    "'": [pug_rule_sq_string],
    "#": [pug_rule_css_id, pug_rule_interpolation],
    ".": [pug_rule_css_class],
    "(": [pug_rule_paren_open],
    ")": [pug_rule_paren_close],
    "=": [pug_rule_equals],
    ",": [pug_rule_comma],
    # Pipe must come before | in interpolation.
    "|": [pug_rule_pipe],
    "!": [pug_rule_interpolation],
    # script: and style: delegation (only at start of line).
    "s": [pug_rule_script_block, pug_rule_style_block],
    # Handlebar expressions.
    "{": [pug_rule_handlebar],
    # Vue bind/event shorthands.
    ":": [pug_rule_vue_bind],
    "@": [pug_rule_vue_event],
}
# @+node:swot.20260501214143.1: ** rulesDictDict
# Add keyword / component / directive / attribute matchers for every word-start character.
for _ch in string.ascii_letters + "_":
    if _ch == "v":
        rulesDict1.setdefault(_ch, []).insert(0, pug_rule_vue_directive)
    if _ch.isupper():
        # PascalCase component names take precedence over keywords.
        rulesDict1.setdefault(_ch, []).insert(0, pug_rule_component)
    rulesDict1.setdefault(_ch, []).append(pug_rule_keyword)
    rulesDict1.setdefault(_ch, []).append(pug_rule_attribute)

# Import dict for pug mode.
# importDict = {}

# x.rulesDictDict for pug mode.
rulesDictDict = {
    "pug_main": rulesDict1,
}
# @-others
# @-leo
