# Leo colorizer control file for nqc mode.
# This file is in the public domain.

# Properties for nqc mode.
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

# Attributes dict for nqc_main ruleset.
nqc_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for nqc mode.
attributesDictDict = {
    "nqc_main": nqc_main_attributes_dict,
}

# Keywords dict for nqc_main ruleset.
nqc_main_keywords_dict = {
    "ACQUIRE_OUT_A": "literal2",
    "ACQUIRE_OUT_B": "literal2",
    "ACQUIRE_OUT_C": "literal2",
    "ACQUIRE_SOUND": "literal2",
    "ACQUIRE_USER_1": "literal2",
    "ACQUIRE_USER_2": "literal2",
    "ACQUIRE_USER_3": "literal2",
    "ACQUIRE_USER_4": "literal2",
    "DISPLAY_OUT_A": "literal2",
    "DISPLAY_OUT_B": "literal2",
    "DISPLAY_OUT_C": "literal2",
    "DISPLAY_SENSOR_1": "literal2",
    "DISPLAY_SENSOR_2": "literal2",
    "DISPLAY_SENSOR_3": "literal2",
    "DISPLAY_WATCH": "literal2",
    "EVENT_1_PRESSED": "literal2",
    "EVENT_1_RELEASED": "literal2",
    "EVENT_2_PRESSED": "literal2",
    "EVENT_2_RELEASED": "literal2",
    "EVENT_COUNTER_0": "literal2",
    "EVENT_COUNTER_1": "literal2",
    "EVENT_LIGHT_CLICK": "literal2",
    "EVENT_LIGHT_DOUBLECLICK": "literal2",
    "EVENT_LIGHT_HIGH": "literal2",
    "EVENT_LIGHT_LOW": "literal2",
    "EVENT_LIGHT_NORMAL": "literal2",
    "EVENT_MESSAGE": "literal2",
    "EVENT_TIMER_0": "literal2",
    "EVENT_TIMER_1": "literal2",
    "EVENT_TIMER_2": "literal2",
    "EVENT_TYPE_CLICK": "literal2",
    "EVENT_TYPE_DOUBLECLICK": "literal2",
    "EVENT_TYPE_EDGE": "literal2",
    "EVENT_TYPE_FASTCHANGE": "literal2",
    "EVENT_TYPE_HIGH": "literal2",
    "EVENT_TYPE_LOW": "literal2",
    "EVENT_TYPE_MESSAGE": "literal2",
    "EVENT_TYPE_NORMAL": "literal2",
    "EVENT_TYPE_PRESSED": "literal2",
    "EVENT_TYPE_PULSE": "literal2",
    "EVENT_TYPE_RELEASED": "literal2",
    "NULL": "literal2",
    "OUT_A": "literal2",
    "OUT_B": "literal2",
    "OUT_C": "literal2",
    "OUT_FLOAT": "literal2",
    "OUT_FULL": "literal2",
    "OUT_FWD": "literal2",
    "OUT_HALF": "literal2",
    "OUT_LOW": "literal2",
    "OUT_OFF": "literal2",
    "OUT_ON": "literal2",
    "OUT_REV": "literal2",
    "OUT_TOOGLE": "literal2",
    "SENSOR_1": "literal2",
    "SENSOR_2": "literal2",
    "SENSOR_3": "literal2",
    "SENSOR_CELSIUS": "literal2",
    "SENSOR_EDGE": "literal2",
    "SENSOR_FAHRENHEIT": "literal2",
    "SENSOR_LIGHT": "literal2",
    "SENSOR_MODE_BOOL": "literal2",
    "SENSOR_MODE_CELSIUS": "literal2",
    "SENSOR_MODE_EDGE": "literal2",
    "SENSOR_MODE_FAHRENHEIT": "literal2",
    "SENSOR_MODE_PERCENT": "literal2",
    "SENSOR_MODE_PULSE": "literal2",
    "SENSOR_MODE_RAW": "literal2",
    "SENSOR_MODE_ROTATION": "literal2",
    "SENSOR_PULSE": "literal2",
    "SENSOR_ROTATION": "literal2",
    "SENSOR_TOUCH": "literal2",
    "SENSOR_TYPE_LIGHT": "literal2",
    "SENSOR_TYPE_NONE": "literal2",
    "SENSOR_TYPE_ROTATION": "literal2",
    "SENSOR_TYPE_TEMPERATURE": "literal2",
    "SENSOR_TYPE_TOUCH": "literal2",
    "SERIAL_COMM_4800": "literal2",
    "SERIAL_COMM_76KHZ": "literal2",
    "SERIAL_COMM_DEFAULT": "literal2",
    "SERIAL_COMM_DUTY25": "literal2",
    "SERIAL_PACKET_": "literal2",
    "SERIAL_PACKET_CHECKSUM": "literal2",
    "SERIAL_PACKET_DEFAULT": "literal2",
    "SERIAL_PACKET_NEGATED": "literal2",
    "SERIAL_PACKET_PREAMBLE": "literal2",
    "SERIAL_PACKET_RCX": "literal2",
    "SOUND_CLICK": "literal2",
    "SOUND_DOUBLE_BEEP": "literal2",
    "SOUND_DOWN": "literal2",
    "SOUND_FAST_UP": "literal2",
    "SOUND_LOW_BEEP": "literal2",
    "SOUND_UP": "literal2",
    "TX_POWER_HI": "literal2",
    "TX_POWER_LO": "literal2",
    "__event_src": "keyword1",
    "__sensor": "keyword1",
    "__type": "keyword1",
    "abs": "keyword1",
    "aquire": "keyword1",
    "asm": "keyword2",
    "break": "keyword1",
    "case": "keyword1",
    "catch": "keyword1",
    "const": "keyword1",
    "continue": "keyword1",
    "default": "keyword1",
    "do": "keyword1",
    "else": "keyword1",
    "false": "literal2",
    "for": "keyword1",
    "if": "keyword1",
    "inline": "keyword2",
    "int": "keyword3",
    "monitor": "keyword1",
    "repeat": "keyword1",
    "return": "keyword1",
    "sign": "keyword1",
    "start": "keyword1",
    "stop": "keyword1",
    "sub": "keyword1",
    "switch": "keyword1",
    "task": "keyword1",
    "true": "literal2",
    "void": "keyword3",
    "while": "keyword1",
}

# Dictionary of keywords dictionaries for nqc mode.
keywordsDictDict = {
    "nqc_main": nqc_main_keywords_dict,
}

# Rules for nqc_main ruleset.

def nqc_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def nqc_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def nqc_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def nqc_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#")

def nqc_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def nqc_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def nqc_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def nqc_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def nqc_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def nqc_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def nqc_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def nqc_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def nqc_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def nqc_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def nqc_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def nqc_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def nqc_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def nqc_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def nqc_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def nqc_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def nqc_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def nqc_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def nqc_rule22(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def nqc_rule23(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def nqc_rule24(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for nqc_main ruleset.
rulesDict1 = {
    "!": [nqc_rule6,],
    "\"": [nqc_rule1,],
    "#": [nqc_rule3,],
    "%": [nqc_rule15,],
    "&": [nqc_rule16,],
    "'": [nqc_rule2,],
    "(": [nqc_rule23,],
    "*": [nqc_rule12,],
    "+": [nqc_rule9,],
    "-": [nqc_rule10,],
    "/": [nqc_rule0, nqc_rule4, nqc_rule11,],
    "0": [nqc_rule24,],
    "1": [nqc_rule24,],
    "2": [nqc_rule24,],
    "3": [nqc_rule24,],
    "4": [nqc_rule24,],
    "5": [nqc_rule24,],
    "6": [nqc_rule24,],
    "7": [nqc_rule24,],
    "8": [nqc_rule24,],
    "9": [nqc_rule24,],
    ":": [nqc_rule22,],
    "<": [nqc_rule8, nqc_rule14,],
    "=": [nqc_rule5,],
    ">": [nqc_rule7, nqc_rule13,],
    "@": [nqc_rule24,],
    "A": [nqc_rule24,],
    "B": [nqc_rule24,],
    "C": [nqc_rule24,],
    "D": [nqc_rule24,],
    "E": [nqc_rule24,],
    "F": [nqc_rule24,],
    "G": [nqc_rule24,],
    "H": [nqc_rule24,],
    "I": [nqc_rule24,],
    "J": [nqc_rule24,],
    "K": [nqc_rule24,],
    "L": [nqc_rule24,],
    "M": [nqc_rule24,],
    "N": [nqc_rule24,],
    "O": [nqc_rule24,],
    "P": [nqc_rule24,],
    "Q": [nqc_rule24,],
    "R": [nqc_rule24,],
    "S": [nqc_rule24,],
    "T": [nqc_rule24,],
    "U": [nqc_rule24,],
    "V": [nqc_rule24,],
    "W": [nqc_rule24,],
    "X": [nqc_rule24,],
    "Y": [nqc_rule24,],
    "Z": [nqc_rule24,],
    "^": [nqc_rule18,],
    "_": [nqc_rule24,],
    "a": [nqc_rule24,],
    "b": [nqc_rule24,],
    "c": [nqc_rule24,],
    "d": [nqc_rule24,],
    "e": [nqc_rule24,],
    "f": [nqc_rule24,],
    "g": [nqc_rule24,],
    "h": [nqc_rule24,],
    "i": [nqc_rule24,],
    "j": [nqc_rule24,],
    "k": [nqc_rule24,],
    "l": [nqc_rule24,],
    "m": [nqc_rule24,],
    "n": [nqc_rule24,],
    "o": [nqc_rule24,],
    "p": [nqc_rule24,],
    "q": [nqc_rule24,],
    "r": [nqc_rule24,],
    "s": [nqc_rule24,],
    "t": [nqc_rule24,],
    "u": [nqc_rule24,],
    "v": [nqc_rule24,],
    "w": [nqc_rule24,],
    "x": [nqc_rule24,],
    "y": [nqc_rule24,],
    "z": [nqc_rule24,],
    "{": [nqc_rule21,],
    "|": [nqc_rule17,],
    "}": [nqc_rule20,],
    "~": [nqc_rule19,],
}

# x.rulesDictDict for nqc mode.
rulesDictDict = {
    "nqc_main": rulesDict1,
}

# Import dict for nqc mode.
importDict = {}
