# Leo colorizer control file for objectrexx mode.
# This file is in the public domain.

# Properties for objectrexx mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "indentNextLines": "\\s*(if|loop|do|else|select|otherwise|catch|finally|class|method|properties)(.*)",
    "lineComment": "--",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for objectrexx_main ruleset.
objectrexx_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0x[[:xdigit:]]+[lL]?|[[:digit:]]+(e[[:digit:]]*)?[lLdDfF]?)",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for objectrexx mode.
attributesDictDict = {
    "objectrexx_main": objectrexx_main_attributes_dict,
}

# Keywords dict for objectrexx_main ruleset.
objectrexx_main_keywords_dict = {
    "Abbrev": "keyword2",
    "Abs": "keyword2",
    "Address": "keyword2",
    "Arg": "keyword2",
    "B2X": "keyword2",
    "Beep": "keyword2",
    "BitAnd": "keyword2",
    "BitOr": "keyword2",
    "BitXor": "keyword2",
    "C2D": "keyword2",
    "C2X": "keyword2",
    "Call": "keyword1",
    "Center": "keyword2",
    "ChangeStr": "keyword2",
    "CharIn": "keyword2",
    "CharOut": "keyword2",
    "Chars": "keyword2",
    "Class": "keyword1",
    "Compare": "keyword2",
    "Consition": "keyword2",
    "Copies": "keyword2",
    "CountStr": "keyword2",
    "D2C": "keyword2",
    "D2X": "keyword2",
    "DataType": "keyword2",
    "Date": "keyword2",
    "DelStr": "keyword2",
    "DelWord": "keyword2",
    "Digits": "keyword2",
    "Directory": "keyword2",
    "Do": "keyword1",
    "Drop": "keyword1",
    "ErrorText": "keyword2",
    "Exit": "keyword1",
    "Expose": "keyword1",
    "FileSpec": "keyword2",
    "Form": "keyword2",
    "Format": "keyword2",
    "Forward": "keyword1",
    "Fuzz": "keyword2",
    "Guard": "keyword1",
    "If": "keyword1",
    "Insert": "keyword2",
    "Interpret": "keyword1",
    "Iterate": "keyword1",
    "LastPos": "keyword2",
    "Leave": "keyword1",
    "Left": "keyword2",
    "Length": "keyword2",
    "LineIn": "keyword2",
    "LineOut": "keyword2",
    "Lines": "keyword2",
    "Max": "keyword2",
    "Method": "keyword1",
    "Min": "keyword2",
    "Nop": "keyword1",
    "Numeric": "keyword1",
    "Overlay": "keyword2",
    "Parse": "keyword1",
    "Pos": "keyword2",
    "Procedure": "keyword1",
    "Push": "keyword1",
    "Queue": "keyword1",
    "Queued": "keyword2",
    "RC": "keyword1",
    "Raise": "keyword1",
    "Random": "keyword2",
    "Requires": "keyword1",
    "Result": "keyword1",
    "Return": "keyword1",
    "Reverse": "keyword2",
    "Right": "keyword2",
    "Routine": "keyword1",
    "RxFuncAdd": "keyword2",
    "RxFuncDrop": "keyword2",
    "RxFuncQuery": "keyword2",
    "RxMessageBox": "keyword2",
    "RxWinExec": "keyword2",
    "Say": "keyword1",
    "Seleect": "keyword1",
    "Self": "keyword1",
    "Sigl": "keyword1",
    "Sign": "keyword2",
    "Signal": "keyword1",
    "SourceLine": "keyword2",
    "Space": "keyword2",
    "Stream": "keyword2",
    "Strip": "keyword2",
    "SubStr": "keyword2",
    "SubWord": "keyword2",
    "Super": "keyword1",
    "Symbol": "keyword2",
    "SysAddRexxMacro": "keyword2",
    "SysBootDrive": "keyword2",
    "SysClearRexxMacroSpace": "keyword2",
    "SysCloseEventSem": "keyword2",
    "SysCloseMutexSem": "keyword2",
    "SysCls": "keyword2",
    "SysCreateEventSem": "keyword2",
    "SysCreateMutexSem": "keyword2",
    "SysCurPos": "keyword2",
    "SysCurState": "keyword2",
    "SysDriveInfo": "keyword2",
    "SysDriveMap": "keyword2",
    "SysDropFuncs": "keyword2",
    "SysDropRexxMacro": "keyword2",
    "SysDumpVariables": "keyword2",
    "SysFileDelete": "keyword2",
    "SysFileSearch": "keyword2",
    "SysFileSystemType": "keyword2",
    "SysFileTree": "keyword2",
    "SysFromUnicode": "keyword2",
    "SysGetErrortext": "keyword2",
    "SysGetFileDateTime": "keyword2",
    "SysGetKey": "keyword2",
    "SysIni": "keyword2",
    "SysLoadFuncs": "keyword2",
    "SysLoadRexxMacroSpace": "keyword2",
    "SysMkDir": "keyword2",
    "SysOpenEventSem": "keyword2",
    "SysOpenMutexSem": "keyword2",
    "SysPostEventSem": "keyword2",
    "SysPulseEventSem": "keyword2",
    "SysQueryProcess": "keyword2",
    "SysQueryRexxMacro": "keyword2",
    "SysReleaseMutexSem": "keyword2",
    "SysReorderRexxMacro": "keyword2",
    "SysRequestMutexSem": "keyword2",
    "SysResetEventSem": "keyword2",
    "SysRmDir": "keyword2",
    "SysSaveRexxMacroSpace": "keyword2",
    "SysSearchPath": "keyword2",
    "SysSetFileDateTime": "keyword2",
    "SysSetPriority": "keyword2",
    "SysSleep": "keyword2",
    "SysStemCopy": "keyword2",
    "SysStemDelete": "keyword2",
    "SysStemInsert": "keyword2",
    "SysStemSort": "keyword2",
    "SysSwitchSession": "keyword2",
    "SysSystemDirectory": "keyword2",
    "SysTempFileName": "keyword2",
    "SysTextScreenRead": "keyword2",
    "SysTextScreenSize": "keyword2",
    "SysToUnicode": "keyword2",
    "SysUtilVersion": "keyword2",
    "SysVersion": "keyword2",
    "SysVolumeLabel": "keyword2",
    "SysWaitEventSem": "keyword2",
    "SysWaitNamedPipe": "keyword2",
    "SysWinDecryptFile": "keyword2",
    "SysWinEncryptFile": "keyword2",
    "SysWinVer": "keyword2",
    "Time": "keyword2",
    "Trace": "keyword2",
    "Translate": "keyword2",
    "Trunc": "keyword2",
    "Value": "keyword2",
    "Var": "keyword2",
    "Verify": "keyword2",
    "Word": "keyword2",
    "WordIndex": "keyword2",
    "WordLength": "keyword2",
    "WordPos": "keyword2",
    "Words": "keyword2",
    "X2B": "keyword2",
    "X2C": "keyword2",
    "X2D": "keyword2",
    "XRange": "keyword2",
    "pull": "keyword1",
    "reply": "keyword1",
    "use": "keyword1",
}

# Dictionary of keywords dictionaries for objectrexx mode.
keywordsDictDict = {
    "objectrexx_main": objectrexx_main_keywords_dict,
}

# Rules for objectrexx_main ruleset.

def objectrexx_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def objectrexx_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def objectrexx_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def objectrexx_rule3(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="keyword2", seq="#")

def objectrexx_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def objectrexx_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def objectrexx_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def objectrexx_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def objectrexx_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def objectrexx_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def objectrexx_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def objectrexx_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def objectrexx_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def objectrexx_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def objectrexx_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def objectrexx_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def objectrexx_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def objectrexx_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def objectrexx_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def objectrexx_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def objectrexx_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def objectrexx_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def objectrexx_rule22(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="::")

def objectrexx_rule23(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_whitespace_end=True,
          exclude_match=True)

def objectrexx_rule24(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def objectrexx_rule25(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for objectrexx_main ruleset.
rulesDict1 = {
    "!": [objectrexx_rule6,],
    "\"": [objectrexx_rule1,],
    "#": [objectrexx_rule3,],
    "%": [objectrexx_rule15,],
    "&": [objectrexx_rule16,],
    "'": [objectrexx_rule2,],
    "(": [objectrexx_rule24,],
    "*": [objectrexx_rule12,],
    "+": [objectrexx_rule9,],
    "-": [objectrexx_rule4, objectrexx_rule10,],
    "/": [objectrexx_rule0, objectrexx_rule11,],
    "0": [objectrexx_rule25,],
    "1": [objectrexx_rule25,],
    "2": [objectrexx_rule25,],
    "3": [objectrexx_rule25,],
    "4": [objectrexx_rule25,],
    "5": [objectrexx_rule25,],
    "6": [objectrexx_rule25,],
    "7": [objectrexx_rule25,],
    "8": [objectrexx_rule25,],
    "9": [objectrexx_rule25,],
    ":": [objectrexx_rule22, objectrexx_rule23,],
    "<": [objectrexx_rule8, objectrexx_rule14,],
    "=": [objectrexx_rule5,],
    ">": [objectrexx_rule7, objectrexx_rule13,],
    "@": [objectrexx_rule25,],
    "A": [objectrexx_rule25,],
    "B": [objectrexx_rule25,],
    "C": [objectrexx_rule25,],
    "D": [objectrexx_rule25,],
    "E": [objectrexx_rule25,],
    "F": [objectrexx_rule25,],
    "G": [objectrexx_rule25,],
    "H": [objectrexx_rule25,],
    "I": [objectrexx_rule25,],
    "J": [objectrexx_rule25,],
    "K": [objectrexx_rule25,],
    "L": [objectrexx_rule25,],
    "M": [objectrexx_rule25,],
    "N": [objectrexx_rule25,],
    "O": [objectrexx_rule25,],
    "P": [objectrexx_rule25,],
    "Q": [objectrexx_rule25,],
    "R": [objectrexx_rule25,],
    "S": [objectrexx_rule25,],
    "T": [objectrexx_rule25,],
    "U": [objectrexx_rule25,],
    "V": [objectrexx_rule25,],
    "W": [objectrexx_rule25,],
    "X": [objectrexx_rule25,],
    "Y": [objectrexx_rule25,],
    "Z": [objectrexx_rule25,],
    "^": [objectrexx_rule18,],
    "a": [objectrexx_rule25,],
    "b": [objectrexx_rule25,],
    "c": [objectrexx_rule25,],
    "d": [objectrexx_rule25,],
    "e": [objectrexx_rule25,],
    "f": [objectrexx_rule25,],
    "g": [objectrexx_rule25,],
    "h": [objectrexx_rule25,],
    "i": [objectrexx_rule25,],
    "j": [objectrexx_rule25,],
    "k": [objectrexx_rule25,],
    "l": [objectrexx_rule25,],
    "m": [objectrexx_rule25,],
    "n": [objectrexx_rule25,],
    "o": [objectrexx_rule25,],
    "p": [objectrexx_rule25,],
    "q": [objectrexx_rule25,],
    "r": [objectrexx_rule25,],
    "s": [objectrexx_rule25,],
    "t": [objectrexx_rule25,],
    "u": [objectrexx_rule25,],
    "v": [objectrexx_rule25,],
    "w": [objectrexx_rule25,],
    "x": [objectrexx_rule25,],
    "y": [objectrexx_rule25,],
    "z": [objectrexx_rule25,],
    "{": [objectrexx_rule21,],
    "|": [objectrexx_rule17,],
    "}": [objectrexx_rule20,],
    "~": [objectrexx_rule19,],
}

# x.rulesDictDict for objectrexx mode.
rulesDictDict = {
    "objectrexx_main": rulesDict1,
}

# Import dict for objectrexx mode.
importDict = {}
