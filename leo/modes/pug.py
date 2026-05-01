# @+leo-ver=5-thin
# @+node:ekr.20250501.1: * @file ../modes/pug.py
"""
leo/modes/pug.py: Leo's mode file for @language pug.

Supports:
- Comments: //- (non-output), // (output)
- Tag names (div, p, a, etc.)
- CSS selectors (#id, .class)
- HTML attributes with double/single quoted strings
- Backslash line continuation in double-quoted strings: "foo \\n  bar \\n  baz"
- Interpolation: #{}, !{}
- Pug directives: doctype, if/else/each/mixin/include/block/extends/case/when/default/append/prepend
- Embedded script: and style: blocks delegating to javascript/css
- Keywords: true/false/and/or/not/null/undefined

Design notes on cross-line strings:
  leo's match_span uses a 'dots' hack for continued strings which
  suppresses setRestart.  This means lines after a backslash-\n
  lose all colouring until the closing quote.  We therefore use a
  custom matcher for "..." that calls setRestart explicitly.
"""

from __future__ import annotations
import re
from typing import Any
from leo.core import leoGlobals as g

assert g


# @+<< pug.py: rules >>
# @+node:ekr.20250501.2: ** << pug.py: rules >>
# @+others
# @+node:ekr.20250501.3: *3* pug_rule_comment_buf //-
def pug_rule_comment_buf(colorer: Any, s: str, i: int) -> int:
    """Match buffer-only (non-output) Pug comment: //-"""
    return colorer.match_eol_span(s, i, kind="comment1", seq="//-")


# @+node:ekr.20250501.4: *3* pug_rule_comment // <!-- output comment -->
def pug_rule_comment(colorer: Any, s: str, i: int) -> int:
    """Match output Pug comment: //"""
    # Must not match //- (handled by pug_rule_comment_buf first).
    return colorer.match_eol_span(s, i, kind="comment1", seq="//")


# @+node:ekr.20250501.6: *3* pug_rule_interpolation
def pug_rule_interpolation(colorer: Any, s: str, i: int) -> int:
    """Match Pug interpolation: #{...} or !{...}"""
    n = colorer.match_span(s, i, kind="literal3", begin="#{", end="}")
    if n:
        return n
    return colorer.match_span(s, i, kind="literal3", begin="!{", end="}")


# @+node:ekr.20250501.7: *3* pug_rule_css_id
def pug_rule_css_id(colorer: Any, s: str, i: int) -> int:
    """Match CSS id selector: #id"""
    if i > 0 and s[i - 1] not in (' ', '\t', '\n', '('):
        return 0
    m = re.match(r'#[a-zA-Z_][a-zA-Z0-9_-]*', s[i:])
    if m:
        colorer.colorRangeWithTag(s, i, i + m.end(), tag="keyword2")
        return m.end()
    return 0


# @+node:ekr.20250501.8: *3* pug_rule_css_class
def pug_rule_css_class(colorer: Any, s: str, i: int) -> int:
    """Match CSS class selector: .class"""
    if i > 0 and s[i - 1] not in (' ', '\t', '\n', '('):
        return 0
    m = re.match(r'\.[a-zA-Z_][a-zA-Z0-9_-]*', s[i:])
    if m:
        colorer.colorRangeWithTag(s, i, i + m.end(), tag="keyword3")
        return m.end()
    return 0


# @+node:ekr.20250501.9: *3* pug_rule_paren_open
def pug_rule_paren_open(colorer: Any, s: str, i: int) -> int:
    """Match opening parenthesis: ( - colored as markup."""
    return colorer.match_seq(s, i, kind="markup", seq="(")


# @+node:ekr.20250501.10: *3* pug_rule_paren_close
def pug_rule_paren_close(colorer: Any, s: str, i: int) -> int:
    """Match closing parenthesis: ) - colored as markup."""
    return colorer.match_seq(s, i, kind="markup", seq=")")


# @+node:ekr.20250501.15: *3* pug_rule_dq_string
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
                return k + 1
            else:
                k += 1
        # Still continuing past this line – re-arm the restart.
        colorer.colorRangeWithTag(s, 0, len(s), tag="literal1")
        colorer.setRestart(restart_dq_string)
        return len(s) + 1

    colorer.setRestart(restart_dq_string)
    return len(s) - i


# @+node:ekr.20250501.16: *3* pug_rule_sq_string
def pug_rule_sq_string(colorer: Any, s: str, i: int) -> int:
    """Match single-quoted string."""
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")


# @+node:ekr.20250501.17: *3* pug_rule_equals
def pug_rule_equals(colorer: Any, s: str, i: int) -> int:
    """Match = operator in attribute."""
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")


# @+node:ekr.20250501.18: *3* pug_rule_comma
def pug_rule_comma(colorer: Any, s: str, i: int) -> int:
    """Match comma separator in attributes."""
    return colorer.match_seq(s, i, kind="operator", seq=",")


# @+node:ekr.20250501.10: *3* pug_rule_script_block
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


# @+node:ekr.20250501.11: *3* pug_rule_style_block
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


# @+node:ekr.20250501.12: *3* pug_rule_doctype
def pug_rule_doctype(colorer: Any, s: str, i: int) -> int:
    """Match doctype declaration."""
    if i == 0 and s.startswith("doctype"):
        colorer.match_seq(s, i, kind="keyword1", seq="doctype")
        return len(s)
    return 0


# @+node:ekr.20250501.13: *3* pug_rule_pipe
def pug_rule_pipe(colorer: Any, s: str, i: int) -> int:
    """Match pipe character | for raw text."""
    if i == 0 and s.startswith("|"):
        colorer.match_seq(s, i, kind="operator", seq="|")
        return len(s)
    return 0


# @-others
# @-<< pug.py: rules >>


# @+<< pug.py: dictionaries >>
# @+node:ekr.20250501.19: ** << pug.py: dictionaries >>
# @+others
# @+node:ekr.20250501.20: *3* pug.py: Properties dict
properties = {
    "commentEnd": "",
    "commentStart": "//-",
}

# @+node:ekr.20250501.21: *3* pug.py: Attributes dicts
pug_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

attributesDictDict = {
    "pug_main": pug_main_attributes_dict,
}
# @+node:ekr.20250501.22: *3* pug.py: Keywords dicts
pug_main_keywords_dict = {
    # HTML tag keywords - colored as markup
    "a": "markup",
    "abbr": "markup",
    "address": "markup",
    "area": "markup",
    "article": "markup",
    "aside": "markup",
    "audio": "markup",
    "b": "markup",
    "base": "markup",
    "bdi": "markup",
    "bdo": "markup",
    "blockquote": "markup",
    "body": "markup",
    "br": "markup",
    "button": "markup",
    "canvas": "markup",
    "caption": "markup",
    "cite": "markup",
    "code": "markup",
    "col": "markup",
    "colgroup": "markup",
    "data": "markup",
    "datalist": "markup",
    "dd": "markup",
    "del": "markup",
    "details": "markup",
    "dfn": "markup",
    "dialog": "markup",
    "div": "markup",
    "dl": "markup",
    "dt": "markup",
    "em": "markup",
    "embed": "markup",
    "fieldset": "markup",
    "figcaption": "markup",
    "figure": "markup",
    "footer": "markup",
    "form": "markup",
    "h1": "markup",
    "h2": "markup",
    "h3": "markup",
    "h4": "markup",
    "h5": "markup",
    "h6": "markup",
    "head": "markup",
    "header": "markup",
    "hgroup": "markup",
    "hr": "markup",
    "html": "markup",
    "i": "markup",
    "iframe": "markup",
    "img": "markup",
    "input": "markup",
    "ins": "markup",
    "kbd": "markup",
    "label": "markup",
    "legend": "markup",
    "li": "markup",
    "link": "markup",
    "main": "markup",
    "map": "markup",
    "mark": "markup",
    "menu": "markup",
    "meta": "markup",
    "meter": "markup",
    "nav": "markup",
    "noscript": "markup",
    "object": "markup",
    "ol": "markup",
    "optgroup": "markup",
    "option": "markup",
    "output": "markup",
    "p": "markup",
    "picture": "markup",
    "pre": "markup",
    "progress": "markup",
    "q": "markup",
    "rp": "markup",
    "rt": "markup",
    "ruby": "markup",
    "s": "markup",
    "samp": "markup",
    "script": "markup",
    "section": "markup",
    "select": "markup",
    "slot": "markup",
    "small": "markup",
    "source": "markup",
    "span": "markup",
    "strong": "markup",
    "style": "markup",
    "sub": "markup",
    "summary": "markup",
    "sup": "markup",
    "table": "markup",
    "tbody": "markup",
    "td": "markup",
    "template": "markup",
    "textarea": "markup",
    "tfoot": "markup",
    "th": "markup",
    "thead": "markup",
    "time": "markup",
    "title": "markup",
    "tr": "markup",
    "track": "markup",
    "u": "markup",
    "ul": "markup",
    "var": "markup",
    "video": "markup",
    "wbr": "markup",
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
}

keywordsDictDict = {
    "pug_main": pug_main_keywords_dict,
}
# @+node:ekr.20250501.23: *3* pug.py: Rules dicts
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
}
# @-others

# Import dict for pug mode.
importDict = {}

# x.rulesDictDict for pug mode.
rulesDictDict = {
    "pug_main": rulesDict1,
}

# @-<< pug.py: dictionaries >>

# @@language python
# @@tabwidth -4
# @-leo
