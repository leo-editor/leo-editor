# Leo colorizer control file for velocity mode.
# This file is in the public domain.

# Properties for velocity mode.
properties = {
    "commentEnd": "*#",
    "commentStart": "#*",
    "lineComment": "##",
}

# Attributes dict for velocity_main ruleset.
velocity_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for velocity_velocity ruleset.
velocity_velocity_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for velocity_javascript ruleset.
velocity_javascript_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for velocity_javascript2 ruleset.
velocity_javascript2_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for velocity_back_to_html ruleset.
velocity_back_to_html_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for velocity_css ruleset.
velocity_css_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for velocity_css2 ruleset.
velocity_css2_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "[[:digit:]]+(pt|pc|in|mm|cm|em|ex|px|ms|s|%)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "-_",
}

# Dictionary of attributes dictionaries for velocity mode.
attributesDictDict = {
    "velocity_back_to_html": velocity_back_to_html_attributes_dict,
    "velocity_css": velocity_css_attributes_dict,
    "velocity_css2": velocity_css2_attributes_dict,
    "velocity_javascript": velocity_javascript_attributes_dict,
    "velocity_javascript2": velocity_javascript2_attributes_dict,
    "velocity_main": velocity_main_attributes_dict,
    "velocity_velocity": velocity_velocity_attributes_dict,
}

# Keywords dict for velocity_main ruleset.
velocity_main_keywords_dict = {}

# Keywords dict for velocity_velocity ruleset.
velocity_velocity_keywords_dict = {
    "#else": "keyword1",
    "#elseif": "keyword1",
    "#end": "keyword1",
    "#foreach": "keyword1",
    "#if": "keyword1",
    "#include": "keyword1",
    "#macro": "keyword1",
    "#parse": "keyword1",
    "#set": "keyword1",
    "#stop": "keyword1",
}

# Keywords dict for velocity_javascript ruleset.
velocity_javascript_keywords_dict = {}

# Keywords dict for velocity_javascript2 ruleset.
velocity_javascript2_keywords_dict = {}

# Keywords dict for velocity_back_to_html ruleset.
velocity_back_to_html_keywords_dict = {}

# Keywords dict for velocity_css ruleset.
velocity_css_keywords_dict = {}

# Keywords dict for velocity_css2 ruleset.
velocity_css2_keywords_dict = {}

# Dictionary of keywords dictionaries for velocity mode.
keywordsDictDict = {
    "velocity_back_to_html": velocity_back_to_html_keywords_dict,
    "velocity_css": velocity_css_keywords_dict,
    "velocity_css2": velocity_css2_keywords_dict,
    "velocity_javascript": velocity_javascript_keywords_dict,
    "velocity_javascript2": velocity_javascript2_keywords_dict,
    "velocity_main": velocity_main_keywords_dict,
    "velocity_velocity": velocity_velocity_keywords_dict,
}

# Rules for velocity_main ruleset.

def velocity_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def velocity_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
          delegate="velocity::javascript")

def velocity_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
          delegate="velocity::css")

def velocity_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
          delegate="xml::dtd-tags")

def velocity_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="html::tags")

def velocity_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)


# Rules dict for velocity_main ruleset.
rulesDict1 = {
    "&": [velocity_rule5,],
    "<": [velocity_rule0, velocity_rule1, velocity_rule2, velocity_rule3, velocity_rule4,],
}

# Rules for velocity_velocity ruleset.

def velocity_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="comment2", begin="#*", end="*#")

def velocity_rule7(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment3", seq="##")

def velocity_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="${", end="}",
          no_line_break=True)

def velocity_rule9(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword3", pattern="$!")

def velocity_rule10(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword3", pattern="$")

def velocity_rule11(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for velocity_velocity ruleset.
rulesDict2 = {
    "#": [velocity_rule6, velocity_rule7, velocity_rule11,],
    "$": [velocity_rule8, velocity_rule9, velocity_rule10,],
    "0": [velocity_rule11,],
    "1": [velocity_rule11,],
    "2": [velocity_rule11,],
    "3": [velocity_rule11,],
    "4": [velocity_rule11,],
    "5": [velocity_rule11,],
    "6": [velocity_rule11,],
    "7": [velocity_rule11,],
    "8": [velocity_rule11,],
    "9": [velocity_rule11,],
    "@": [velocity_rule11,],
    "A": [velocity_rule11,],
    "B": [velocity_rule11,],
    "C": [velocity_rule11,],
    "D": [velocity_rule11,],
    "E": [velocity_rule11,],
    "F": [velocity_rule11,],
    "G": [velocity_rule11,],
    "H": [velocity_rule11,],
    "I": [velocity_rule11,],
    "J": [velocity_rule11,],
    "K": [velocity_rule11,],
    "L": [velocity_rule11,],
    "M": [velocity_rule11,],
    "N": [velocity_rule11,],
    "O": [velocity_rule11,],
    "P": [velocity_rule11,],
    "Q": [velocity_rule11,],
    "R": [velocity_rule11,],
    "S": [velocity_rule11,],
    "T": [velocity_rule11,],
    "U": [velocity_rule11,],
    "V": [velocity_rule11,],
    "W": [velocity_rule11,],
    "X": [velocity_rule11,],
    "Y": [velocity_rule11,],
    "Z": [velocity_rule11,],
    "a": [velocity_rule11,],
    "b": [velocity_rule11,],
    "c": [velocity_rule11,],
    "d": [velocity_rule11,],
    "e": [velocity_rule11,],
    "f": [velocity_rule11,],
    "g": [velocity_rule11,],
    "h": [velocity_rule11,],
    "i": [velocity_rule11,],
    "j": [velocity_rule11,],
    "k": [velocity_rule11,],
    "l": [velocity_rule11,],
    "m": [velocity_rule11,],
    "n": [velocity_rule11,],
    "o": [velocity_rule11,],
    "p": [velocity_rule11,],
    "q": [velocity_rule11,],
    "r": [velocity_rule11,],
    "s": [velocity_rule11,],
    "t": [velocity_rule11,],
    "u": [velocity_rule11,],
    "v": [velocity_rule11,],
    "w": [velocity_rule11,],
    "x": [velocity_rule11,],
    "y": [velocity_rule11,],
    "z": [velocity_rule11,],
}

# Rules for velocity_javascript ruleset.

def velocity_rule12(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=">",
          delegate="velocity::javascript2")

def velocity_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq="SRC=",
          delegate="velocity::back_to_html")

# Rules dict for velocity_javascript ruleset.
rulesDict3 = {
    ">": [velocity_rule12,],
    "S": [velocity_rule13,],
}

# Rules for velocity_javascript2 ruleset.



# Rules dict for velocity_javascript2 ruleset.
rulesDict4 = {}

# Rules for velocity_back_to_html ruleset.

def velocity_rule14(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=">",
          delegate="velocity::main")

# Rules dict for velocity_back_to_html ruleset.
rulesDict5 = {
    ">": [velocity_rule14,],
}

# Rules for velocity_css ruleset.

def velocity_rule15(colorer, s, i):
    return colorer.match_seq(s, i, kind="markup", seq=">",
          delegate="velocity::css2")

# Rules dict for velocity_css ruleset.
rulesDict6 = {
    ">": [velocity_rule15,],
}

# Rules for velocity_css2 ruleset.



# Rules dict for velocity_css2 ruleset.
rulesDict7 = {}

# x.rulesDictDict for velocity mode.
rulesDictDict = {
    "velocity_back_to_html": rulesDict5,
    "velocity_css": rulesDict6,
    "velocity_css2": rulesDict7,
    "velocity_javascript": rulesDict3,
    "velocity_javascript2": rulesDict4,
    "velocity_main": rulesDict1,
    "velocity_velocity": rulesDict2,
}

# Import dict for velocity mode.
importDict = {
    "velocity_css2": ["velocity_css2::velocity", "css::main",],
    "velocity_javascript2": ["velocity_javascript2::velocity", "javascript::main",],
    "velocity_main": ["velocity_main::velocity",],
}
