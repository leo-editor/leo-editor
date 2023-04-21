# Leo colorizer control file for groovy mode.
# This file is in the public domain.

# Properties for groovy mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "indentCloseBrackets": "}",
    "indentNextLine": "\\s*(((if|while)\\s*\\(|else\\s*|else\\s+if\\s*\\(|for\\s*\\(.*\\))[^{;]*)",
    "indentOpenBrackets": "{",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
}

# Attributes dict for groovy_main ruleset.
groovy_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for groovy_literal ruleset.
groovy_literal_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for groovy_groovydoc ruleset.
groovy_groovydoc_attributes_dict = {
    "default": "COMMENT3",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for groovy mode.
attributesDictDict = {
    "groovy_groovydoc": groovy_groovydoc_attributes_dict,
    "groovy_literal": groovy_literal_attributes_dict,
    "groovy_main": groovy_main_attributes_dict,
}

# Keywords dict for groovy_main ruleset.
groovy_main_keywords_dict = {
    "abs": "keyword4",
    "abstract": "keyword1",
    "any": "keyword4",
    "append": "keyword4",
    "as": "keyword2",
    "asList": "keyword4",
    "asWritable": "keyword4",
    "assert": "keyword2",
    "boolean": "keyword3",
    "break": "keyword1",
    "byte": "keyword3",
    "call": "keyword4",
    "case": "keyword1",
    "catch": "keyword1",
    "char": "keyword3",
    "class": "keyword3",
    "collect": "keyword4",
    "compareTo": "keyword4",
    "const": "invalid",
    "continue": "keyword1",
    "count": "keyword4",
    "def": "keyword2",
    "default": "keyword1",
    "div": "keyword4",
    "do": "keyword1",
    "double": "keyword3",
    "dump": "keyword4",
    "each": "keyword4",
    "eachByte": "keyword4",
    "eachFile": "keyword4",
    "eachLine": "keyword4",
    "else": "keyword1",
    "every": "keyword4",
    "extends": "keyword1",
    "false": "literal2",
    "final": "keyword1",
    "finally": "keyword1",
    "find": "keyword4",
    "findAll": "keyword4",
    "flatten": "keyword4",
    "float": "keyword3",
    "for": "keyword1",
    "getAt": "keyword4",
    "getErr": "keyword4",
    "getIn": "keyword4",
    "getOut": "keyword4",
    "getText": "keyword4",
    "goto": "invalid",
    "grep": "keyword4",
    "if": "keyword1",
    "immutable": "keyword4",
    "implements": "keyword1",
    "import": "keyword1",
    "in": "keyword2",
    "inject": "keyword4",
    "inspect": "keyword4",
    "instanceof": "keyword1",
    "int": "keyword3",
    "interface": "keyword3",
    "intersect": "keyword4",
    "invokeMethods": "keyword4",
    "isCase": "keyword4",
    "it": "literal3",
    "join": "keyword4",
    "leftShift": "keyword4",
    "long": "keyword3",
    "minus": "keyword4",
    "mixin": "keyword2",
    "multiply": "keyword4",
    "native": "keyword1",
    "new": "keyword1",
    "newInputStream": "keyword4",
    "newOutputStream": "keyword4",
    "newPrintWriter": "keyword4",
    "newReader": "keyword4",
    "newWriter": "keyword4",
    "next": "keyword4",
    "null": "literal2",
    "package": "keyword1",
    "plus": "keyword4",
    "pop": "keyword4",
    "power": "keyword4",
    "previous": "keyword4",
    "print": "keyword4",
    "println": "keyword4",
    "private": "keyword1",
    "property": "keyword2",
    "protected": "keyword1",
    "public": "keyword1",
    "push": "keyword4",
    "putAt": "keyword4",
    "read": "keyword4",
    "readBytes": "keyword4",
    "readLines": "keyword4",
    "return": "keyword1",
    "reverse": "keyword4",
    "reverseEach": "keyword4",
    "round": "keyword4",
    "short": "keyword3",
    "size": "keyword4",
    "sort": "keyword4",
    "splitEachLine": "keyword4",
    "static": "keyword1",
    "step": "keyword4",
    "strictfp": "keyword1",
    "subMap": "keyword4",
    "super": "literal2",
    "switch": "keyword1",
    "synchronized": "keyword1",
    "test": "keyword2",
    "this": "literal2",
    "throw": "keyword1",
    "throws": "keyword1",
    "times": "keyword4",
    "toInteger": "keyword4",
    "toList": "keyword4",
    "tokenize": "keyword4",
    "transient": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "upto": "keyword4",
    "using": "keyword2",
    "void": "keyword3",
    "volatile": "keyword1",
    "waitForOrKill": "keyword4",
    "while": "keyword1",
    "withPrintWriter": "keyword4",
    "withReader": "keyword4",
    "withStream": "keyword4",
    "withWriter": "keyword4",
    "withWriterAppend": "keyword4",
    "write": "keyword4",
    "writeLine": "keyword4",
}

# Keywords dict for groovy_literal ruleset.
groovy_literal_keywords_dict = {}

# Keywords dict for groovy_groovydoc ruleset.
groovy_groovydoc_keywords_dict = {}

# Dictionary of keywords dictionaries for groovy mode.
keywordsDictDict = {
    "groovy_groovydoc": groovy_groovydoc_keywords_dict,
    "groovy_literal": groovy_literal_keywords_dict,
    "groovy_main": groovy_main_keywords_dict,
}

# Rules for groovy_main ruleset.

def groovy_rule0(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment1", seq="/**/")

def groovy_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="groovy::groovydoc")

def groovy_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def groovy_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="groovy::literal")

def groovy_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def groovy_rule5(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal1", begin="<<<([[:alpha:]_][[:alnum:]_]*)\\s*", end="$1",
          delegate="groovy::literal")

def groovy_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=~")

def groovy_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def groovy_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def groovy_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def groovy_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=>")

def groovy_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def groovy_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def groovy_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def groovy_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="->")

def groovy_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def groovy_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def groovy_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def groovy_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=".*")

def groovy_rule19(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="//")

def groovy_rule20(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def groovy_rule21(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for groovy_main ruleset.
rulesDict1 = {
    "!": [groovy_rule9,],
    "\"": [groovy_rule3,],
    "&": [groovy_rule17,],
    "'": [groovy_rule4,],
    "(": [groovy_rule20,],
    "+": [groovy_rule13,],
    "-": [groovy_rule14, groovy_rule15,],
    ".": [groovy_rule18,],
    "/": [groovy_rule0, groovy_rule1, groovy_rule2, groovy_rule19,],
    "0": [groovy_rule21,],
    "1": [groovy_rule21,],
    "2": [groovy_rule21,],
    "3": [groovy_rule21,],
    "4": [groovy_rule21,],
    "5": [groovy_rule21,],
    "6": [groovy_rule21,],
    "7": [groovy_rule21,],
    "8": [groovy_rule21,],
    "9": [groovy_rule21,],
    "<": [groovy_rule5, groovy_rule10, groovy_rule12,],
    "=": [groovy_rule6, groovy_rule7,],
    ">": [groovy_rule11,],
    "?": [groovy_rule16,],
    "@": [groovy_rule21,],
    "A": [groovy_rule21,],
    "B": [groovy_rule21,],
    "C": [groovy_rule21,],
    "D": [groovy_rule21,],
    "E": [groovy_rule21,],
    "F": [groovy_rule21,],
    "G": [groovy_rule21,],
    "H": [groovy_rule21,],
    "I": [groovy_rule21,],
    "J": [groovy_rule21,],
    "K": [groovy_rule21,],
    "L": [groovy_rule21,],
    "M": [groovy_rule21,],
    "N": [groovy_rule21,],
    "O": [groovy_rule21,],
    "P": [groovy_rule21,],
    "Q": [groovy_rule21,],
    "R": [groovy_rule21,],
    "S": [groovy_rule21,],
    "T": [groovy_rule21,],
    "U": [groovy_rule21,],
    "V": [groovy_rule21,],
    "W": [groovy_rule21,],
    "X": [groovy_rule21,],
    "Y": [groovy_rule21,],
    "Z": [groovy_rule21,],
    "a": [groovy_rule21,],
    "b": [groovy_rule21,],
    "c": [groovy_rule21,],
    "d": [groovy_rule21,],
    "e": [groovy_rule21,],
    "f": [groovy_rule21,],
    "g": [groovy_rule21,],
    "h": [groovy_rule21,],
    "i": [groovy_rule21,],
    "j": [groovy_rule21,],
    "k": [groovy_rule21,],
    "l": [groovy_rule21,],
    "m": [groovy_rule21,],
    "n": [groovy_rule21,],
    "o": [groovy_rule21,],
    "p": [groovy_rule21,],
    "q": [groovy_rule21,],
    "r": [groovy_rule21,],
    "s": [groovy_rule21,],
    "t": [groovy_rule21,],
    "u": [groovy_rule21,],
    "v": [groovy_rule21,],
    "w": [groovy_rule21,],
    "x": [groovy_rule21,],
    "y": [groovy_rule21,],
    "z": [groovy_rule21,],
    "|": [groovy_rule8,],
}

# Rules for groovy_literal ruleset.

def groovy_rule22(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          no_line_break=True)

def groovy_rule23(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="keyword2", pattern="$")

# Rules dict for groovy_literal ruleset.
rulesDict2 = {
    "$": [groovy_rule22, groovy_rule23,],
}

# Rules for groovy_groovydoc ruleset.

def groovy_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="{")

def groovy_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="*")

def groovy_rule26(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def groovy_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="<<")

def groovy_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="<=")

def groovy_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="< ")

def groovy_rule30(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="xml::tags",
          no_line_break=True)

def groovy_rule31(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="label", pattern="@")

# Rules dict for groovy_groovydoc ruleset.
rulesDict3 = {
    "*": [groovy_rule25,],
    "<": [groovy_rule26, groovy_rule27, groovy_rule28, groovy_rule29, groovy_rule30,],
    "@": [groovy_rule31,],
    "{": [groovy_rule24,],
}

# x.rulesDictDict for groovy mode.
rulesDictDict = {
    "groovy_groovydoc": rulesDict3,
    "groovy_literal": rulesDict2,
    "groovy_main": rulesDict1,
}

# Import dict for groovy mode.
importDict = {}
