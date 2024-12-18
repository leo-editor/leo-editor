#@+leo-ver=5-thin
#@+node:ekr.20241119064750.1: * @file ../modes/css.py
"""
leo/modes/css.py: Leo's mode file for @language css.
"""
#@+<< css.py: imports >>
#@+node:ekr.20241120011923.1: ** << css.py: imports >>
from __future__ import annotations
from typing import Any
from leo.core import leoGlobals as g
assert g
#@-<< css.py: imports >>
#@+<< css.py rules >>
#@+node:ekr.20241120010414.1: ** << css.py rules >>
#@+others
#@+node:ekr.20241119185920.1: *3* css.py: rules for css_main ruleset
#@+node:ekr.20241120174607.1: *4* css_rule0
def css_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")
#@+node:ekr.20241120174607.2: *4* css_rule1
def css_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=";")
#@+node:ekr.20241120174607.3: *4* css_rule2 (..)
def css_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="null", begin="(", end=")",
          delegate="css::literal")
#@+node:ekr.20241120174607.4: *4* css_rule3
def css_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")
#@+node:ekr.20241120174607.5: *4* css_rule4
def css_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")
#@+node:ekr.20241120174607.6: *4* css_rule5
def css_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=",")
#@+node:ekr.20241120174607.7: *4* css_rule6
def css_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=".")
#@+node:ekr.20241120174607.8: *4* css_rule7
def css_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")
#@+node:ekr.20241120174607.9: *4* css_rule8
def css_rule8(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern="#")
#@+node:ekr.20241120174607.10: *4* css_rule8A
# For selectors...

def css_rule8A(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern=".")
#@+node:ekr.20241120174607.11: *4* css_rule8B
def css_rule8B(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern=">")
#@+node:ekr.20241120174607.12: *4* css_rule8C
def css_rule8C(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern="+")
#@+node:ekr.20241120174607.13: *4* css_rule8D
def css_rule8D(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal2", pattern="~")
#@+node:ekr.20241120174607.14: *4* css_rule9
def css_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")
#@+node:ekr.20241120174607.15: *4* css_rule10
def css_rule10(colorer, s, i):
    return colorer.match_keywords(s, i)
#@+node:ekr.20241121083146.1: *4* css_rule_at_language @language
def css_rule_at_language(colorer, s, i):

    if i == 0 and s.startswith("@language "):
        return colorer.match_at_language(s, i)
    return 0  # Fail, but allow other matches.
#@+node:ekr.20241120174643.1: *4* css_rule_end_style </style>
def css_rule_end_style(colorer: Any, s: str, i: int) -> int:

    if i != 0 or not s.startswith("</style>"):
        return 0  # Fail, but allow other matches.

    # Colorize the element as an html element..
    colorer.match_seq(s, i, kind="markup", seq="</style>", delegate="html")

    # Restart any previous delegate.
    colorer.pop_delegate()
    return len(s)  # Success.
#@+node:ekr.20241121083900.1: *4* css_rule_style <style>
def css_rule_style(colorer: Any, s: str, i: int) -> int:

    if i != 0 or not s.startswith("<style"):
        return 0  # Fail, but allow other matches.

    # Colorize the element as an html element..
    colorer.match_span(s, i, kind="markup", begin="<style", end=">", delegate="html")

    # Start css mode.
    colorer.push_delegate('css')
    return len(s)  # Success.

#@-others
#@-<< css.py rules >>
#@+<< css.py dictionaries >>
#@+node:ekr.20241120010446.1: ** << css.py dictionaries >>
#@+others
#@+node:ekr.20241119185711.1: *3* css.py: attributes dicts
# Attributes dict for css_main ruleset.
css_main_attributes_dict = {
    "default": "null",
    "digit_re": "-?[[:digit:]]+(pt|pc|in|mm|cm|em|ex|px|ms|s|%)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "-_%",
}

# Attributes dict for css_literal ruleset.
css_literal_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "-?[[:digit:]]+(pt|pc|in|mm|cm|em|ex|px|ms|s|%)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "-_%",
}

# Dictionary of attributes dictionaries for css mode.
attributesDictDict = {
    "css_literal": css_literal_attributes_dict,
    "css_main": css_main_attributes_dict,
}
#@+node:ekr.20241119185615.1: *3* css.py: properties dict
# Properties for css mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineUpClosingBracket": "true",
    "noWordSep": "_",
}
#@+node:ekr.20241119185813.1: *3* css.py: keywords dict for css_main ruleset
# Keywords dict for css_main ruleset.
css_main_keywords_dict = {
    ":after": "keyword3",
    ":before": "keyword3",
    "@font-face": "keyword2",
    "@import": "keyword2",
    "@media": "keyword2",
    "@page": "keyword2",
    "above": "keyword3",
    "absolute": "keyword3",
    "aliceblue": "keyword3",
    "always": "keyword3",
    "antiquewhite": "keyword3",
    "aqua": "keyword3",
    "aquamarine": "keyword3",
    "armenian": "keyword3",
    "ascent": "keyword2",
    "auto": "keyword3",
    "avoid": "keyword3",
    "azimuth": "keyword2",
    "azure": "keyword3",
    "background": "keyword2",
    "background-attachment": "keyword2",
    "background-color": "keyword2",
    "background-image": "keyword2",
    "background-position": "keyword2",
    "background-repeat": "keyword2",
    "baseline": "keyword3",
    "behind": "keyword3",
    "beige": "keyword3",
    "below": "keyword3",
    "bidi-override": "keyword3",
    "bisque": "keyword3",
    "black": "keyword3",
    "blanchedalmond": "keyword3",
    "blink": "keyword3",
    "block": "keyword3",
    "blue": "keyword3",
    "blueviolet": "keyword3",
    "bold": "keyword3",
    "bolder": "keyword3",
    "border": "keyword2",
    "border-bottom": "keyword2",
    "border-bottom-color": "keyword2",
    "border-bottom-style": "keyword2",
    "border-bottom-width": "keyword2",
    "border-collapse": "keyword2",
    "border-color": "keyword2",
    "border-left": "keyword2",
    "border-left-color": "keyword2",
    "border-left-style": "keyword2",
    "border-left-width": "keyword2",
    "border-right": "keyword2",
    "border-right-color": "keyword2",
    "border-right-style": "keyword2",
    "border-right-width": "keyword2",
    "border-spacing": "keyword2",
    "border-style": "keyword2",
    "border-top": "keyword2",
    "border-top-color": "keyword2",
    "border-top-style": "keyword2",
    "border-top-width": "keyword2",
    "border-width": "keyword2",
    "both": "keyword3",
    "bottom": "keyword3",
    "brown": "keyword3",
    "burlywood": "keyword3",
    "cadetblue": "keyword3",
    "cap-height": "keyword2",
    "capitalize": "keyword3",
    "caption-side": "keyword2",
    "center": "keyword3",
    "center-left": "keyword3",
    "center-right": "keyword3",
    "centerline": "keyword2",
    "chartreuse": "keyword3",
    "child": "keyword3",
    "chocolate": "keyword3",
    "circle": "keyword3",
    "cjk-ideographic": "keyword3",
    "clear": "keyword2",
    "clip": "keyword2",
    "close-quote": "keyword3",
    "code": "keyword3",
    "collapse": "keyword3",
    "color": "keyword2",
    "compact": "keyword3",
    "condensed": "keyword3",
    "content": "keyword2",
    "continuous": "keyword3",
    "coral": "keyword3",
    "cornflowerblue": "keyword3",
    "cornsilk": "keyword3",
    "counter-increment": "keyword2",
    "counter-reset": "keyword2",
    "crimson": "keyword3",
    "crop": "keyword3",
    "cross": "keyword3",
    "crosshair": "keyword3",
    "cue": "keyword2",
    "cue-after": "keyword3",
    "cue-before": "keyword3",
    "cursor": "keyword2",
    "cyan": "keyword3",
    "darkblue": "keyword3",
    "darkcyan": "keyword3",
    "darkgoldenrod": "keyword3",
    "darkgray": "keyword3",
    "darkgreen": "keyword3",
    "darkgrey": "keyword3",
    "darkkhaki": "keyword3",
    "darkmagenta": "keyword3",
    "darkolivegreen": "keyword3",
    "darkorange": "keyword3",
    "darkorchid": "keyword3",
    "darkpink": "keyword3",
    "darkred": "keyword3",
    "darksalmon": "keyword3",
    "darkseagreen": "keyword3",
    "darkslateblue": "keyword3",
    "darkslategray": "keyword3",
    "darkslategrey": "keyword3",
    "darkturquoise": "keyword3",
    "darkviolet": "keyword3",
    "dashed": "keyword3",
    "decimal": "keyword3",
    "decimal-leading-zero": "keyword3",
    "deepskyblue": "keyword3",
    "default": "keyword3",
    "definition-src": "keyword2",
    "descent": "keyword2",
    "digits": "keyword3",
    "dimgray": "keyword3",
    "dimgrey": "keyword3",
    "direction": "keyword2",
    "disc": "keyword3",
    "display": "keyword2",
    "dodgerblue": "keyword3",
    "dotted": "keyword3",
    "double": "keyword3",
    "e-resize": "keyword3",
    "elevation": "keyword2",
    "embed": "keyword3",
    "empty-cells": "keyword2",
    "expanded": "keyword3",
    "extra-condensed": "keyword3",
    "extra-expanded": "keyword3",
    "far-left": "keyword3",
    "far-right": "keyword3",
    "fast": "keyword3",
    "faster": "keyword3",
    "female": "keyword3",
    "firebrick": "keyword3",
    "fixed": "keyword3",
    "float": "keyword2",
    "floralwhite": "keyword3",
    "font": "keyword2",
    "font-family": "keyword2",
    "font-size": "keyword2",
    "font-size-adjust": "keyword2",
    "font-stretch": "keyword2",
    "font-style": "keyword2",
    "font-variant": "keyword2",
    "font-weight": "keyword2",
    "forestgreen": "keyword3",
    "fushia": "keyword3",
    "gainsboro": "keyword3",
    "georgian": "keyword3",
    "ghostwhite": "keyword3",
    "gold": "keyword3",
    "goldenrod": "keyword3",
    "gray": "keyword3",
    "green": "keyword3",
    "greenyellow": "keyword3",
    "grey": "keyword3",
    "groove": "keyword3",
    "hebrew": "keyword3",
    "height": "keyword2",
    "help": "keyword3",
    "hidden": "keyword3",
    "hide": "keyword3",
    "high": "keyword3",
    "higher": "keyword3",
    "hiragana": "keyword3",
    "hiragana-iroha": "keyword3",
    "honeydew": "keyword3",
    "hotpink": "keyword3",
    "indianred": "keyword3",
    "indigo": "keyword3",
    "inherit": "keyword3",
    "inline": "keyword3",
    "inline-table": "keyword3",
    "inset": "keyword3",
    "inside": "keyword3",
    "invert": "keyword3",
    "italic": "keyword3",
    "ivory": "keyword3",
    "katakana": "keyword3",
    "katakana-iroha": "keyword3",
    "khaki": "keyword3",
    "landscape": "keyword3",
    "large": "keyword3",
    "larger": "keyword3",
    "lavender": "keyword3",
    "lavenderblush": "keyword3",
    "lawngreen": "keyword3",
    "left": "keyword2",
    "left-side": "keyword3",
    "leftwards": "keyword3",
    "lemonchiffon": "keyword3",
    "letter-spacing": "keyword2",
    "level": "keyword3",
    "lightblue": "keyword3",
    "lightcoral": "keyword3",
    "lightcyan": "keyword3",
    "lighter": "keyword3",
    "lightgoldenrodyellow": "keyword3",
    "lightgray": "keyword3",
    "lightgreen": "keyword3",
    "lightgrey": "keyword3",
    "lightpink": "keyword3",
    "lightsalmon": "keyword3",
    "lightseagreen": "keyword3",
    "lightskyblue": "keyword3",
    "lightslategray": "keyword3",
    "lightslategrey": "keyword3",
    "lightsteelblue": "keyword3",
    "lightyellow": "keyword3",
    "lime": "keyword3",
    "limegreen": "keyword3",
    "line-height": "keyword2",
    "line-through": "keyword3",
    "linen": "keyword3",
    "list-item": "keyword3",
    "list-style": "keyword2",
    "list-style-image": "keyword2",
    "list-style-position": "keyword2",
    "list-style-type": "keyword2",
    "loud": "keyword3",
    "low": "keyword3",
    "lower": "keyword3",
    "lower-alpha": "keyword3",
    "lower-greek": "keyword3",
    "lower-latin": "keyword3",
    "lower-roman": "keyword3",
    "lowercase": "keyword3",
    "ltr": "keyword3",
    "magenta": "keyword3",
    "male": "keyword3",
    "margin": "keyword2",
    "margin-bottom": "keyword2",
    "margin-left": "keyword2",
    "margin-right": "keyword2",
    "margin-top": "keyword2",
    "marker": "keyword3",
    "marker-offset": "keyword2",
    "marks": "keyword2",
    "maroon": "keyword3",
    "mathline": "keyword2",
    "max-height": "keyword2",
    "max-width": "keyword2",
    "medium": "keyword3",
    "mediumaquamarine": "keyword3",
    "mediumblue": "keyword3",
    "mediumorchid": "keyword3",
    "mediumpurple": "keyword3",
    "mediumseagreen": "keyword3",
    "mediumslateblue": "keyword3",
    "mediumspringgreen": "keyword3",
    "mediumturquoise": "keyword3",
    "mediumvioletred": "keyword3",
    "middle": "keyword3",
    "midnightblue": "keyword3",
    "min-height": "keyword2",
    "min-width": "keyword2",
    "mintcream": "keyword3",
    "mistyrose": "keyword3",
    "mix": "keyword3",
    "mocassin": "keyword3",
    "move": "keyword3",
    "n-resize": "keyword3",
    "narrower": "keyword3",
    "navawhite": "keyword3",
    "navy": "keyword3",
    "ne-resize": "keyword3",
    "no-close-quote": "keyword3",
    "no-open-quote": "keyword3",
    "no-repeat": "keyword3",
    "none": "keyword3",
    "normal": "keyword3",
    "nowrap": "keyword3",
    "nw-resize": "keyword3",
    "oblique": "keyword3",
    "oldlace": "keyword3",
    "olidrab": "keyword3",
    "olive": "keyword3",
    "once": "keyword3",
    "open-quote": "keyword3",
    "orange": "keyword3",
    "orangered": "keyword3",
    "orchid": "keyword3",
    "orphans": "keyword2",
    "outline": "keyword2",
    "outline-color": "keyword2",
    "outline-style": "keyword2",
    "outline-width": "keyword2",
    "outset": "keyword3",
    "outside": "keyword3",
    "overflow": "keyword2",
    "overline": "keyword3",
    "padding": "keyword2",
    "padding-bottom": "keyword2",
    "padding-left": "keyword2",
    "padding-right": "keyword2",
    "padding-top": "keyword2",
    "page": "keyword2",
    "page-break-after": "keyword2",
    "page-break-before": "keyword2",
    "page-break-inside": "keyword2",
    "palegoldenrod": "keyword3",
    "palegreen": "keyword3",
    "paleturquoise": "keyword3",
    "paletvioletred": "keyword3",
    "panose-1": "keyword2",
    "papayawhip": "keyword3",
    "pause": "keyword2",
    "pause-after": "keyword2",
    "pause-before": "keyword2",
    "peachpuff": "keyword3",
    "peru": "keyword3",
    "pink": "keyword3",
    "pitch": "keyword2",
    "pitch-range": "keyword2",
    "play-during": "keyword2",
    "plum": "keyword3",
    "pointer": "keyword3",
    "portrait": "keyword3",
    "position": "keyword2",
    "powderblue": "keyword3",
    "pre": "keyword3",
    "purple": "keyword3",
    "quotes": "keyword2",
    "red": "keyword3",
    "relative": "keyword3",
    "repeat": "keyword3",
    "repeat-x": "keyword3",
    "repeat-y": "keyword3",
    "rgb": "keyword3",
    "richness": "keyword2",
    "ridge": "keyword3",
    "right": "keyword3",
    "right-side": "keyword3",
    "rightwards": "keyword3",
    "rosybrown": "keyword3",
    "royalblue": "keyword3",
    "rtl": "keyword3",
    "run-in": "keyword3",
    "s-resize": "keyword3",
    "saddlebrown": "keyword3",
    "salmon": "keyword3",
    "sandybrown": "keyword3",
    "scroll": "keyword3",
    "se-resize": "keyword3",
    "seagreen": "keyword3",
    "seashell": "keyword3",
    "semi-condensed": "keyword3",
    "semi-expanded": "keyword3",
    "separate": "keyword3",
    "show": "keyword3",
    "sienna": "keyword3",
    "silent": "keyword3",
    "silver": "keyword3",
    "size": "keyword2",
    "skyblue": "keyword3",
    "slateblue": "keyword3",
    "slategray": "keyword3",
    "slategrey": "keyword3",
    "slope": "keyword2",
    "slow": "keyword3",
    "slower": "keyword3",
    "small": "keyword3",
    "small-caps": "keyword3",
    "smaller": "keyword3",
    "snow": "keyword3",
    "soft": "keyword3",
    "solid": "keyword3",
    "speak": "keyword2",
    "speak-header-cell": "keyword2",
    "speak-headers": "keyword2",
    "speak-numeral": "keyword2",
    "speak-punctuation": "keyword2",
    "speech-rate": "keyword2",
    "spell-out": "keyword3",
    "springgreen": "keyword3",
    "square": "keyword3",
    "src": "keyword2",
    "static": "keyword3",
    "steelblue": "keyword3",
    "stemh": "keyword2",
    "stemv": "keyword2",
    "stress": "keyword2",
    "sub": "keyword3",
    "super": "keyword3",
    "sw-resize": "keyword3",
    "table": "keyword3",
    "table-caption": "keyword3",
    "table-cell": "keyword3",
    "table-column": "keyword3",
    "table-column-group": "keyword3",
    "table-footer-group": "keyword3",
    "table-header-group": "keyword3",
    "table-layout": "keyword2",
    "table-row": "keyword3",
    "table-row-group": "keyword3",
    "tan": "keyword3",
    "teal": "keyword3",
    "text": "keyword3",
    "text-align": "keyword2",
    "text-bottom": "keyword3",
    "text-decoration": "keyword2",
    "text-indent": "keyword2",
    "text-shadow": "keyword2",
    "text-top": "keyword3",
    "text-transform": "keyword2",
    "thick": "keyword3",
    "thin": "keyword3",
    "thistle": "keyword3",
    "tomato": "keyword3",
    "top": "keyword3",
    "topline": "keyword2",
    "transparent": "keyword3",
    "turquoise": "keyword3",
    "ultra-condensed": "keyword3",
    "ultra-expanded": "keyword3",
    "underline": "keyword3",
    "unicode-bidi": "keyword2",
    "unicode-range": "keyword2",
    "units-per-em": "keyword2",
    "upper-alpha": "keyword3",
    "upper-latin": "keyword3",
    "upper-roman": "keyword3",
    "uppercase": "keyword3",
    "url": "keyword3",
    "vertical-align": "keyword2",
    "violet": "keyword3",
    "visibility": "keyword2",
    "visible": "keyword3",
    "voice-family": "keyword2",
    "volume": "keyword2",
    "w-resize": "keyword3",
    "wait": "keyword3",
    "wheat": "keyword3",
    "white": "keyword3",
    "white-space": "keyword2",
    "whitesmoke": "keyword3",
    "wider": "keyword3",
    "widows": "keyword2",
    "width": "keyword2",
    "word-spacing": "keyword2",
    "x-fast": "keyword3",
    "x-height": "keyword2",
    "x-high": "keyword3",
    "x-large": "keyword3",
    "x-loud": "keyword3",
    "x-low": "keyword3",
    "x-slow": "keyword3",
    "x-small": "keyword3",
    "xx-large": "keyword3",
    "xx-small": "keyword3",
    "yellow": "keyword3",
    "yellowgreen": "keyword3",
    "z-index": "keyword2",
}
#@+node:ekr.20241119190054.1: *3* css.py: rules dict for css_main ruleset
# Rules dict for css_main ruleset.
rulesDict1 = {
    "!": [css_rule7],
    "#": [css_rule8],
    "(": [css_rule2],
    ",": [css_rule5],
    "-": [css_rule10],
    ".": [css_rule8A],  # Fix #585. Was css_rule6
    "<": [
        css_rule_style,
        css_rule_end_style,
    ],
    ">": [css_rule8B],  # Fix #585.
    "+": [css_rule8C],  # Fix #585.
    "~": [css_rule8D],  # Fix #585.
    "/": [css_rule9],
    "0": [css_rule10],
    "1": [css_rule10],
    "2": [css_rule10],
    "3": [css_rule10],
    "4": [css_rule10],
    "5": [css_rule10],
    "6": [css_rule10],
    "7": [css_rule10],
    "8": [css_rule10],
    "9": [css_rule10],
    ":": [css_rule0, css_rule10],
    ";": [css_rule1],
    "@": [
            css_rule_at_language,
            css_rule10,
        ],
    "A": [css_rule10],
    "B": [css_rule10],
    "C": [css_rule10],
    "D": [css_rule10],
    "E": [css_rule10],
    "F": [css_rule10],
    "G": [css_rule10],
    "H": [css_rule10],
    "I": [css_rule10],
    "J": [css_rule10],
    "K": [css_rule10],
    "L": [css_rule10],
    "M": [css_rule10],
    "N": [css_rule10],
    "O": [css_rule10],
    "P": [css_rule10],
    "Q": [css_rule10],
    "R": [css_rule10],
    "S": [css_rule10],
    "T": [css_rule10],
    "U": [css_rule10],
    "V": [css_rule10],
    "W": [css_rule10],
    "X": [css_rule10],
    "Y": [css_rule10],
    "Z": [css_rule10],
    "a": [css_rule10],
    "b": [css_rule10],
    "c": [css_rule10],
    "d": [css_rule10],
    "e": [css_rule10],
    "f": [css_rule10],
    "g": [css_rule10],
    "h": [css_rule10],
    "i": [css_rule10],
    "j": [css_rule10],
    "k": [css_rule10],
    "l": [css_rule10],
    "m": [css_rule10],
    "n": [css_rule10],
    "o": [css_rule10],
    "p": [css_rule10],
    "q": [css_rule10],
    "r": [css_rule10],
    "s": [css_rule10],
    "t": [css_rule10],
    "u": [css_rule10],
    "v": [css_rule10],
    "w": [css_rule10],
    "x": [css_rule10],
    "y": [css_rule10],
    "z": [css_rule10],
    "{": [css_rule3],
    "}": [css_rule4],
}
#@+node:ekr.20241119190259.1: *3* css.py: css_literal ruleset (empty)
# Rules for css_literal ruleset.

# Rules dict for css_literal ruleset.
rulesDict2 = {}

# Keywords dict for css_literal ruleset.
css_literal_keywords_dict = {}
#@-others

# Import dict for css mode.
importDict = {}

# x.rulesDictDict for css mode.
rulesDictDict = {
    "css_literal": rulesDict2,  # Used only in this file.
    "css_main": rulesDict1,
}

# Dictionary of keywords dictionaries for css mode.
keywordsDictDict = {
    "css_literal": css_literal_keywords_dict,
    "css_main": css_main_keywords_dict,
}
#@-<< css.py dictionaries >>

#@@language python
#@@tabwidth -4
#@-leo
