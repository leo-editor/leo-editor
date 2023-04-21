# Leo colorizer control file for smi_mib mode.
# This file is in the public domain.

# Properties for smi_mib mode.
properties = {
    "indentCloseBrackets": "}",
    "indentNextLines": ".*(::=|AGENT-CAPABILITIES|DESCRIPTION|IMPORTS|MODULE-COMPLIANCE|MODULE-IDENTITY|NOTIFICATION-GROUP|NOTIFICATION-TYPE|OBJECT-GROUP|OBJECT-IDENTITY|OBJECT-TYPE|TEXTUAL-CONVENTION)\\s*$",
    "indentOpenBrackets": "{",
    "lineComment": "--",
    "lineUpClosingBracket": "true",
    "noWordSep": "-",
}

# Attributes dict for smi_mib_main ruleset.
smi_mib_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for smi_mib mode.
attributesDictDict = {
    "smi_mib_main": smi_mib_main_attributes_dict,
}

# Keywords dict for smi_mib_main ruleset.
smi_mib_main_keywords_dict = {
    "ACCESS": "keyword1",
    "AGENT-CAPABILITIES": "function",
    "AUGMENTS": "keyword1",
    "AutonomousType": "keyword2",
    "BEGIN": "function",
    "BITS": "keyword2",
    "CONTACT-INFO": "keyword1",
    "CREATION-REQUIRES": "keyword1",
    "Counter32": "keyword2",
    "Counter64": "keyword2",
    "DEFINITIONS": "keyword1",
    "DEFVAL": "keyword1",
    "DESCRIPTION": "keyword1",
    "DISPLAY-HINT": "keyword1",
    "DateAndTime": "keyword2",
    "DisplayString": "keyword2",
    "END": "function",
    "FROM": "function",
    "GROUP": "keyword1",
    "Gauge32": "keyword2",
    "IMPORTS": "function",
    "INCLUDES": "keyword1",
    "INDEX": "keyword1",
    "INTEGER": "keyword2",
    "InstancePointer": "keyword2",
    "Integer32": "keyword2",
    "IpAddress": "keyword2",
    "LAST-UPDATED": "keyword1",
    "MANDATORY-GROUPS": "keyword1",
    "MAX-ACCESS": "keyword1",
    "MIN-ACCESS": "keyword1",
    "MODULE": "keyword1",
    "MODULE-COMPLIANCE": "function",
    "MODULE-IDENTITY": "function",
    "MacAddress": "keyword2",
    "NOTIFICATION-GROUP": "function",
    "NOTIFICATION-TYPE": "function",
    "NOTIFICATIONS": "keyword1",
    "OBJECT": "keyword1",
    "OBJECT-GROUP": "function",
    "OBJECT-IDENTITY": "function",
    "OBJECT-TYPE": "function",
    "OBJECTS": "keyword1",
    "ORGANIZATION": "keyword1",
    "Opaque": "keyword2",
    "PRODUCT-RELEASE": "keyword1",
    "PhysAddress": "keyword2",
    "REFERENCE": "keyword1",
    "REVISION": "keyword1",
    "RowPointer": "keyword2",
    "RowStatus": "keyword2",
    "SEQUENCE": "keyword2",
    "SIZE": "keyword3",
    "STATUS": "keyword1",
    "SUPPORTS": "keyword1",
    "SYNTAX": "keyword1",
    "StorageType": "keyword2",
    "TAddress": "keyword2",
    "TDomain": "keyword2",
    "TEXTUAL-CONVENTION": "function",
    "TestAndIncr": "keyword2",
    "TimeInterval": "keyword2",
    "TimeStamp": "keyword2",
    "TimeTicks": "keyword2",
    "TruthValue": "keyword2",
    "UNITS": "keyword1",
    "Unsigned32": "keyword2",
    "VARIATION": "keyword1",
    "VariablePointer": "keyword2",
    "WRITE-SYNTAX": "keyword1",
    "accessible-for-notify": "keyword3",
    "current": "keyword3",
    "deprecated": "keyword3",
    "not-accessible": "keyword3",
    "obsolete": "keyword3",
    "read-create": "keyword3",
    "read-only": "keyword3",
    "read-write": "keyword3",
}

# Dictionary of keywords dictionaries for smi_mib mode.
keywordsDictDict = {
    "smi_mib_main": smi_mib_main_keywords_dict,
}

# Rules for smi_mib_main ruleset.

def smi_mib_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def smi_mib_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def smi_mib_rule2(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="::=")

def smi_mib_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def smi_mib_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def smi_mib_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="OBJECT IDENTIFIER")

def smi_mib_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="SEQUENCE OF")

def smi_mib_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="OCTET STRING")

def smi_mib_rule8(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for smi_mib_main ruleset.
rulesDict1 = {
    "\"": [smi_mib_rule1,],
    "-": [smi_mib_rule0, smi_mib_rule8,],
    "0": [smi_mib_rule8,],
    "1": [smi_mib_rule8,],
    "2": [smi_mib_rule8,],
    "3": [smi_mib_rule8,],
    "4": [smi_mib_rule8,],
    "5": [smi_mib_rule8,],
    "6": [smi_mib_rule8,],
    "7": [smi_mib_rule8,],
    "8": [smi_mib_rule8,],
    "9": [smi_mib_rule8,],
    ":": [smi_mib_rule2,],
    "@": [smi_mib_rule8,],
    "A": [smi_mib_rule8,],
    "B": [smi_mib_rule8,],
    "C": [smi_mib_rule8,],
    "D": [smi_mib_rule8,],
    "E": [smi_mib_rule8,],
    "F": [smi_mib_rule8,],
    "G": [smi_mib_rule8,],
    "H": [smi_mib_rule8,],
    "I": [smi_mib_rule8,],
    "J": [smi_mib_rule8,],
    "K": [smi_mib_rule8,],
    "L": [smi_mib_rule8,],
    "M": [smi_mib_rule8,],
    "N": [smi_mib_rule8,],
    "O": [smi_mib_rule5, smi_mib_rule7, smi_mib_rule8,],
    "P": [smi_mib_rule8,],
    "Q": [smi_mib_rule8,],
    "R": [smi_mib_rule8,],
    "S": [smi_mib_rule6, smi_mib_rule8,],
    "T": [smi_mib_rule8,],
    "U": [smi_mib_rule8,],
    "V": [smi_mib_rule8,],
    "W": [smi_mib_rule8,],
    "X": [smi_mib_rule8,],
    "Y": [smi_mib_rule8,],
    "Z": [smi_mib_rule8,],
    "a": [smi_mib_rule8,],
    "b": [smi_mib_rule8,],
    "c": [smi_mib_rule8,],
    "d": [smi_mib_rule8,],
    "e": [smi_mib_rule8,],
    "f": [smi_mib_rule8,],
    "g": [smi_mib_rule8,],
    "h": [smi_mib_rule8,],
    "i": [smi_mib_rule8,],
    "j": [smi_mib_rule8,],
    "k": [smi_mib_rule8,],
    "l": [smi_mib_rule8,],
    "m": [smi_mib_rule8,],
    "n": [smi_mib_rule8,],
    "o": [smi_mib_rule8,],
    "p": [smi_mib_rule8,],
    "q": [smi_mib_rule8,],
    "r": [smi_mib_rule8,],
    "s": [smi_mib_rule8,],
    "t": [smi_mib_rule8,],
    "u": [smi_mib_rule8,],
    "v": [smi_mib_rule8,],
    "w": [smi_mib_rule8,],
    "x": [smi_mib_rule8,],
    "y": [smi_mib_rule8,],
    "z": [smi_mib_rule8,],
    "{": [smi_mib_rule4,],
    "}": [smi_mib_rule3,],
}

# x.rulesDictDict for smi_mib mode.
rulesDictDict = {
    "smi_mib_main": rulesDict1,
}

# Import dict for smi_mib mode.
importDict = {}
