# Leo colorizer control file for typescript mode.
# This file is in the public domain.

# Properties for typescript mode.
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

# Attributes dict for typescript_main ruleset.
typescript_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for typescript mode.
attributesDictDict = {
    "typescript_main": typescript_main_attributes_dict,
}

# Keywords dict for typescript_main ruleset.
typescript_main_keywords_dict = {
    "Array": "keyword3",
    "Boolean": "keyword3",
    "Date": "keyword3",
    "Function": "keyword3",
    "Global": "keyword3",
    "Infinity": "literal2",
    "Math": "keyword3",
    "NaN": "literal2",
    "Number": "keyword3",
    "Object": "keyword3",
    "RegExp": "keyword3",
    "String": "keyword3",
    "abstract": "keyword1",
    "adAsyncExecute": "literal2",
    "adAsyncFetch": "literal2",
    "adAsyncFetchNonBlocking": "literal2",
    "adBSTR": "literal2",
    "adBigInt": "literal2",
    "adBinary": "literal2",
    "adBoolean": "literal2",
    "adChapter": "literal2",
    "adChar": "literal2",
    "adCmdFile": "literal2",
    "adCmdStoredProc": "literal2",
    "adCmdTable": "literal2",
    "adCmdTableDirect": "literal2",
    "adCmdText": "literal2",
    "adCmdUnknown": "literal2",
    "adCurrency": "literal2",
    "adDBDate": "literal2",
    "adDBFileTime": "literal2",
    "adDBTime": "literal2",
    "adDBTimeStamp": "literal2",
    "adDate": "literal2",
    "adDecimal": "literal2",
    "adDouble": "literal2",
    "adEmpty": "literal2",
    "adError": "literal2",
    "adExecuteNoRecords": "literal2",
    "adFileTime": "literal2",
    "adGUID": "literal2",
    "adIDispatch": "literal2",
    "adIUnknown": "literal2",
    "adInteger": "literal2",
    "adLockBatchOptimistic": "literal2",
    "adLockOptimistic": "literal2",
    "adLockPessimistic": "literal2",
    "adLockReadOnly": "literal2",
    "adLongVarBinary": "literal2",
    "adLongVarChar": "literal2",
    "adLongVarWChar": "literal2",
    "adNumeric": "literal2",
    "adOpenDynamic": "literal2",
    "adOpenForwardOnly": "literal2",
    "adOpenKeyset": "literal2",
    "adOpenStatic": "literal2",
    "adParamInput": "literal2",
    "adParamInputOutput": "literal2",
    "adParamLong": "literal2",
    "adParamNullable": "literal2",
    "adParamOutput": "literal2",
    "adParamReturnValue": "literal2",
    "adParamSigned": "literal2",
    "adParamUnknown": "literal2",
    "adPersistADTG": "literal2",
    "adPersistXML": "literal2",
    "adPropVariant": "literal2",
    "adRunAsync": "literal2",
    "adSingle": "literal2",
    "adSmallInt": "literal2",
    "adStateClosed": "literal2",
    "adStateConnecting": "literal2",
    "adStateExecuting": "literal2",
    "adStateFetching": "literal2",
    "adStateOpen": "literal2",
    "adTinyInt": "literal2",
    "adUnsignedBigInt": "literal2",
    "adUnsignedInt": "literal2",
    "adUnsignedSmallInt": "literal2",
    "adUnsignedTinyInt": "literal2",
    "adUseClient": "literal2",
    "adUseServer": "literal2",
    "adUserDefined": "literal2",
    "adVarBinary": "literal2",
    "adVarChar": "literal2",
    "adVarNumeric": "literal2",
    "adVarWChar": "literal2",
    "adVariant": "literal2",
    "adWChar": "literal2",
    "boolean": "keyword3",
    "break": "keyword1",
    "byte": "keyword3",
    "case": "keyword1",
    "catch": "keyword1",
    "char": "keyword3",
    "class": "keyword1",
    "const": "keyword1",
    "continue": "keyword1",
    "debugger": "keyword1",
    "default": "keyword1",
    "delete": "keyword1",
    "do": "keyword1",
    "double": "keyword3",
    "else": "keyword1",
    "enum": "keyword1",
    "escape": "literal2",
    "eval": "literal2",
    "export": "keyword2",
    "extends": "keyword1",
    "false": "literal2",
    "final": "keyword1",
    "finally": "keyword1",
    "float": "keyword3",
    "for": "keyword1",
    "function": "keyword1",
    "goto": "keyword1",
    "if": "keyword1",
    "implements": "keyword1",
    "import": "keyword2",
    "in": "keyword1",
    "instanceof": "keyword1",
    "int": "keyword3",
    "interface": "keyword1",
    "isFinite": "literal2",
    "isNaN": "literal2",
    "long": "keyword3",
    "native": "keyword1",
    "new": "keyword1",
    "null": "literal2",
    "package": "keyword2",
    "parseFloat": "literal2",
    "parseInt": "literal2",
    "private": "keyword1",
    "protected": "keyword1",
    "public": "keyword1",
    "return": "keyword1",
    "short": "keyword3",
    "static": "keyword1",
    "super": "literal2",
    "switch": "keyword1",
    "synchronized": "keyword1",
    "this": "literal2",
    "throw": "keyword1",
    "throws": "keyword1",
    "transient": "keyword1",
    "true": "literal2",
    "try": "keyword1",
    "typeof": "keyword1",
    "unescape": "literal2",
    "var": "keyword1",
    "void": "keyword3",
    "volatile": "keyword1",
    "while": "keyword1",
    "with": "keyword1",
}

# Dictionary of keywords dictionaries for typescript mode.
keywordsDictDict = {
    "typescript_main": typescript_main_keywords_dict,
}

# Rules for typescript_main ruleset.

# #1602
def typescript_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/*", end="*/")

def typescript_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def typescript_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def typescript_rule3(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def typescript_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def typescript_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment1", seq="<!--")

def typescript_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def typescript_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def typescript_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def typescript_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def typescript_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def typescript_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def typescript_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def typescript_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def typescript_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def typescript_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def typescript_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def typescript_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def typescript_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def typescript_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def typescript_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def typescript_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def typescript_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def typescript_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def typescript_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def typescript_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def typescript_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def typescript_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def typescript_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def typescript_rule29(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def typescript_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def typescript_rule31(colorer, s, i):
    return colorer.match_keywords(s, i)

def typescript_rule32(colorer, s, i):  # #2287.
    return colorer.match_span(s, i, kind="literal1", begin="`", end="`",
          no_line_break=True)

# Rules dict for typescript_main ruleset.
rulesDict1 = {
    "`": [typescript_rule32,],  # #2287.
    "!": [typescript_rule7,],
    "\"": [typescript_rule1,],
    "%": [typescript_rule16,],
    "&": [typescript_rule17,],
    "'": [typescript_rule2,],
    "(": [typescript_rule3,],
    "*": [typescript_rule13,],
    "+": [typescript_rule10,],
    ",": [typescript_rule24,],
    "-": [typescript_rule11,],
    ".": [typescript_rule21,],
    "/": [typescript_rule0, typescript_rule4, typescript_rule12,],
    "0": [typescript_rule31,],
    "1": [typescript_rule31,],
    "2": [typescript_rule31,],
    "3": [typescript_rule31,],
    "4": [typescript_rule31,],
    "5": [typescript_rule31,],
    "6": [typescript_rule31,],
    "7": [typescript_rule31,],
    "8": [typescript_rule31,],
    "9": [typescript_rule31,],
    ":": [typescript_rule29, typescript_rule30,],
    ";": [typescript_rule25,],
    "<": [typescript_rule5, typescript_rule9, typescript_rule15,],
    "=": [typescript_rule6,],
    ">": [typescript_rule8, typescript_rule14,],
    "?": [typescript_rule28,],
    "@": [typescript_rule31,],
    "A": [typescript_rule31,],
    "B": [typescript_rule31,],
    "C": [typescript_rule31,],
    "D": [typescript_rule31,],
    "E": [typescript_rule31,],
    "F": [typescript_rule31,],
    "G": [typescript_rule31,],
    "H": [typescript_rule31,],
    "I": [typescript_rule31,],
    "J": [typescript_rule31,],
    "K": [typescript_rule31,],
    "L": [typescript_rule31,],
    "M": [typescript_rule31,],
    "N": [typescript_rule31,],
    "O": [typescript_rule31,],
    "P": [typescript_rule31,],
    "Q": [typescript_rule31,],
    "R": [typescript_rule31,],
    "S": [typescript_rule31,],
    "T": [typescript_rule31,],
    "U": [typescript_rule31,],
    "V": [typescript_rule31,],
    "W": [typescript_rule31,],
    "X": [typescript_rule31,],
    "Y": [typescript_rule31,],
    "Z": [typescript_rule31,],
    "[": [typescript_rule27,],
    "]": [typescript_rule26,],
    "^": [typescript_rule19,],
    "a": [typescript_rule31,],
    "b": [typescript_rule31,],
    "c": [typescript_rule31,],
    "d": [typescript_rule31,],
    "e": [typescript_rule31,],
    "f": [typescript_rule31,],
    "g": [typescript_rule31,],
    "h": [typescript_rule31,],
    "i": [typescript_rule31,],
    "j": [typescript_rule31,],
    "k": [typescript_rule31,],
    "l": [typescript_rule31,],
    "m": [typescript_rule31,],
    "n": [typescript_rule31,],
    "o": [typescript_rule31,],
    "p": [typescript_rule31,],
    "q": [typescript_rule31,],
    "r": [typescript_rule31,],
    "s": [typescript_rule31,],
    "t": [typescript_rule31,],
    "u": [typescript_rule31,],
    "v": [typescript_rule31,],
    "w": [typescript_rule31,],
    "x": [typescript_rule31,],
    "y": [typescript_rule31,],
    "z": [typescript_rule31,],
    "{": [typescript_rule23,],
    "|": [typescript_rule18,],
    "}": [typescript_rule22,],
    "~": [typescript_rule20,],
}

# x.rulesDictDict for typescript mode.
rulesDictDict = {
    "typescript_main": rulesDict1,
}

# Import dict for typescript mode.
importDict = {}
