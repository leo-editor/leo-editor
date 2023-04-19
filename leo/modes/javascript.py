# Leo colorizer control file for javascript mode.
# This file is in the public domain.

# Properties for javascript mode.
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

# Attributes dict for javascript_main ruleset.
javascript_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for javascript mode.
attributesDictDict = {
    "javascript_main": javascript_main_attributes_dict,
}

# Keywords dict for javascript_main ruleset.
javascript_main_keywords_dict = {
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

# Dictionary of keywords dictionaries for javascript mode.
keywordsDictDict = {
    "javascript_main": javascript_main_keywords_dict,
}

# Rules for javascript_main ruleset.

def javascript_rule0(colorer, s, i):
    return colorer.match_span(s, i, "comment1", begin="/*", end="*/")
def javascript_rule1(colorer, s, i):
    return colorer.match_span(s, i, "literal1", begin="\"", end="\"",
        no_line_break=True)
def javascript_rule2(colorer, s, i):
    return colorer.match_span(s, i, "literal1", begin="'", end="'",
        no_line_break=True)
def javascript_rule3(colorer, s, i):
    return colorer.match_mark_previous(s, i, "function", pattern="(",
        exclude_match=True)
def javascript_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, "comment2", seq="//",
        exclude_match=False)
def javascript_rule5(colorer, s, i):
    return colorer.match_seq(s, i, "comment1", seq="<!--")
def javascript_rule6(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="=")
def javascript_rule7(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="!")
def javascript_rule8(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq=">=")
def javascript_rule9(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="<=")
def javascript_rule10(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="+")
def javascript_rule11(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="-")
def javascript_rule12(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="/")
def javascript_rule13(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="*")
def javascript_rule14(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq=">")
def javascript_rule15(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="<")
def javascript_rule16(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="%")
def javascript_rule17(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="&")
def javascript_rule18(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="|")
def javascript_rule19(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="^")
def javascript_rule20(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="~")
def javascript_rule21(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq=".")
def javascript_rule22(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="}")
def javascript_rule23(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="{")
def javascript_rule24(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq=",")
def javascript_rule25(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq=";")
def javascript_rule26(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="]")
def javascript_rule27(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="[")
def javascript_rule28(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq="?")
def javascript_rule29(colorer, s, i):
    return colorer.match_mark_previous(s, i, "label", pattern=":",
        at_whitespace_end=True, exclude_match=True)
def javascript_rule30(colorer, s, i):
    return colorer.match_seq(s, i, "operator", seq=":")
def javascript_rule31(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for javascript_main ruleset.
rulesDict1 = {
    "!": [javascript_rule7,],
    "\"": [javascript_rule1,],
    "%": [javascript_rule16,],
    "&": [javascript_rule17,],
    "'": [javascript_rule2,],
    "(": [javascript_rule3,],
    "*": [javascript_rule13,],
    "+": [javascript_rule10,],
    ",": [javascript_rule24,],
    "-": [javascript_rule11,],
    ".": [javascript_rule21,],
    "/": [javascript_rule0, javascript_rule4, javascript_rule12,],
    "0": [javascript_rule31,],
    "1": [javascript_rule31,],
    "2": [javascript_rule31,],
    "3": [javascript_rule31,],
    "4": [javascript_rule31,],
    "5": [javascript_rule31,],
    "6": [javascript_rule31,],
    "7": [javascript_rule31,],
    "8": [javascript_rule31,],
    "9": [javascript_rule31,],
    ":": [javascript_rule29, javascript_rule30,],
    ";": [javascript_rule25,],
    "<": [javascript_rule5, javascript_rule9, javascript_rule15,],
    "=": [javascript_rule6,],
    ">": [javascript_rule8, javascript_rule14,],
    "?": [javascript_rule28,],
    "@": [javascript_rule31,],
    "A": [javascript_rule31,],
    "B": [javascript_rule31,],
    "C": [javascript_rule31,],
    "D": [javascript_rule31,],
    "E": [javascript_rule31,],
    "F": [javascript_rule31,],
    "G": [javascript_rule31,],
    "H": [javascript_rule31,],
    "I": [javascript_rule31,],
    "J": [javascript_rule31,],
    "K": [javascript_rule31,],
    "L": [javascript_rule31,],
    "M": [javascript_rule31,],
    "N": [javascript_rule31,],
    "O": [javascript_rule31,],
    "P": [javascript_rule31,],
    "Q": [javascript_rule31,],
    "R": [javascript_rule31,],
    "S": [javascript_rule31,],
    "T": [javascript_rule31,],
    "U": [javascript_rule31,],
    "V": [javascript_rule31,],
    "W": [javascript_rule31,],
    "X": [javascript_rule31,],
    "Y": [javascript_rule31,],
    "Z": [javascript_rule31,],
    "[": [javascript_rule27,],
    "]": [javascript_rule26,],
    "^": [javascript_rule19,],
    "a": [javascript_rule31,],
    "b": [javascript_rule31,],
    "c": [javascript_rule31,],
    "d": [javascript_rule31,],
    "e": [javascript_rule31,],
    "f": [javascript_rule31,],
    "g": [javascript_rule31,],
    "h": [javascript_rule31,],
    "i": [javascript_rule31,],
    "j": [javascript_rule31,],
    "k": [javascript_rule31,],
    "l": [javascript_rule31,],
    "m": [javascript_rule31,],
    "n": [javascript_rule31,],
    "o": [javascript_rule31,],
    "p": [javascript_rule31,],
    "q": [javascript_rule31,],
    "r": [javascript_rule31,],
    "s": [javascript_rule31,],
    "t": [javascript_rule31,],
    "u": [javascript_rule31,],
    "v": [javascript_rule31,],
    "w": [javascript_rule31,],
    "x": [javascript_rule31,],
    "y": [javascript_rule31,],
    "z": [javascript_rule31,],
    "{": [javascript_rule23,],
    "|": [javascript_rule18,],
    "}": [javascript_rule22,],
    "~": [javascript_rule20,],
}

# x.rulesDictDict for javascript mode.
rulesDictDict = {
    "javascript_main": rulesDict1,
}

# Import dict for javascript mode.
importDict = {}
