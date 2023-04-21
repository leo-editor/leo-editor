# Leo colorizer control file for scala mode.
# This file is in the public domain.

# Properties for scala mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "doubleBracketIndent": "false",
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "indentPrevLine": "\\s*(((if|while)\\s*\\(|else\\s*(\\{|$)|else\\s+if\\s*\\(|case\\s+.+:|default:)[^;]*|for\\s*\\(.*)",
    "indentSize": "2",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
    "noTabs": "true",
    "tabSize": "2",
    "wordBreakChars": ",+-=<>/?^&*",
}

# Attributes dict for scala_main ruleset.
scala_main_attributes_dict = {
    "default": "null",
    "digit_re": "(0[lL]?|[1-9]\\d{0,9}(\\d{0,9}[lL])?|0[xX]\\p{XDigit}{1,8}(\\p{XDigit}{0,8}[lL])?|0[0-7]{1,11}([0-7]{0,11}[lL])?|([0-9]+\\.[0-9]*|\\.[0-9]+)([eE][+-]?[0-9]+)?[fFdD]?|[0-9]+([eE][+-]?[0-9]+[fFdD]?|([eE][+-]?[0-9]+)?[fFdD]))",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for scala_primary ruleset.
scala_primary_attributes_dict = {
    "default": "null",
    "digit_re": "(0[lL]?|[1-9]\\d{0,9}(\\d{0,9}[lL])?|0[xX]\\p{XDigit}{1,8}(\\p{XDigit}{0,8}[lL])?|0[0-7]{1,11}([0-7]{0,11}[lL])?|([0-9]+\\.[0-9]*|\\.[0-9]+)([eE][+-]?[0-9]+)?[fFdD]?|[0-9]+([eE][+-]?[0-9]+[fFdD]?|([eE][+-]?[0-9]+)?[fFdD]))",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for scala_pattern ruleset.
scala_pattern_attributes_dict = {
    "default": "NULL",
    "digit_re": "(0[lL]?|[1-9]\\d{0,9}(\\d{0,9}[lL])?|0[xX]\\p{XDigit}{1,8}(\\p{XDigit}{0,8}[lL])?|0[0-7]{1,11}([0-7]{0,11}[lL])?|([0-9]+\\.[0-9]*|\\.[0-9]+)([eE][+-]?[0-9]+)?[fFdD]?|[0-9]+([eE][+-]?[0-9]+[fFdD]?|([eE][+-]?[0-9]+)?[fFdD]))",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for scala_scaladoc ruleset.
scala_scaladoc_attributes_dict = {
    "default": "COMMENT3",
    "digit_re": "(0[lL]?|[1-9]\\d{0,9}(\\d{0,9}[lL])?|0[xX]\\p{XDigit}{1,8}(\\p{XDigit}{0,8}[lL])?|0[0-7]{1,11}([0-7]{0,11}[lL])?|([0-9]+\\.[0-9]*|\\.[0-9]+)([eE][+-]?[0-9]+)?[fFdD]?|[0-9]+([eE][+-]?[0-9]+[fFdD]?|([eE][+-]?[0-9]+)?[fFdD]))",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for scala_scaladoc_pre ruleset.
scala_scaladoc_pre_attributes_dict = {
    "default": "COMMENT3",
    "digit_re": "(0[lL]?|[1-9]\\d{0,9}(\\d{0,9}[lL])?|0[xX]\\p{XDigit}{1,8}(\\p{XDigit}{0,8}[lL])?|0[0-7]{1,11}([0-7]{0,11}[lL])?|([0-9]+\\.[0-9]*|\\.[0-9]+)([eE][+-]?[0-9]+)?[fFdD]?|[0-9]+([eE][+-]?[0-9]+[fFdD]?|([eE][+-]?[0-9]+)?[fFdD]))",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for scala_xml_tag ruleset.
scala_xml_tag_attributes_dict = {
    "default": "LABEL",
    "digit_re": "(0[lL]?|[1-9]\\d{0,9}(\\d{0,9}[lL])?|0[xX]\\p{XDigit}{1,8}(\\p{XDigit}{0,8}[lL])?|0[0-7]{1,11}([0-7]{0,11}[lL])?|([0-9]+\\.[0-9]*|\\.[0-9]+)([eE][+-]?[0-9]+)?[fFdD]?|[0-9]+([eE][+-]?[0-9]+[fFdD]?|([eE][+-]?[0-9]+)?[fFdD]))",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for scala_xml_text ruleset.
scala_xml_text_attributes_dict = {
    "default": "COMMENT4",
    "digit_re": "(0[lL]?|[1-9]\\d{0,9}(\\d{0,9}[lL])?|0[xX]\\p{XDigit}{1,8}(\\p{XDigit}{0,8}[lL])?|0[0-7]{1,11}([0-7]{0,11}[lL])?|([0-9]+\\.[0-9]*|\\.[0-9]+)([eE][+-]?[0-9]+)?[fFdD]?|[0-9]+([eE][+-]?[0-9]+[fFdD]?|([eE][+-]?[0-9]+)?[fFdD]))",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for scala_xml_comment ruleset.
scala_xml_comment_attributes_dict = {
    "default": "COMMENT2",
    "digit_re": "(0[lL]?|[1-9]\\d{0,9}(\\d{0,9}[lL])?|0[xX]\\p{XDigit}{1,8}(\\p{XDigit}{0,8}[lL])?|0[0-7]{1,11}([0-7]{0,11}[lL])?|([0-9]+\\.[0-9]*|\\.[0-9]+)([eE][+-]?[0-9]+)?[fFdD]?|[0-9]+([eE][+-]?[0-9]+[fFdD]?|([eE][+-]?[0-9]+)?[fFdD]))",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for scala mode.
attributesDictDict = {
    "scala_main": scala_main_attributes_dict,
    "scala_pattern": scala_pattern_attributes_dict,
    "scala_primary": scala_primary_attributes_dict,
    "scala_scaladoc": scala_scaladoc_attributes_dict,
    "scala_scaladoc_pre": scala_scaladoc_pre_attributes_dict,
    "scala_xml_comment": scala_xml_comment_attributes_dict,
    "scala_xml_tag": scala_xml_tag_attributes_dict,
    "scala_xml_text": scala_xml_text_attributes_dict,
}

# Keywords dict for scala_main ruleset.
scala_main_keywords_dict = {}

# Keywords dict for scala_primary ruleset.
scala_primary_keywords_dict = {

### EKR
#    "\t  ": "",
#    "\n": "",
#    "    ": "",
#    "      ": "",
    "=": "",
    ">": "",
    "Actor": "",
    "ActorProxy": "",
    "ActorTask": "",
    "ActorThread": "",
    "AllRef": "",
    "Any": "",
    "AnyRef": "",
    "Application": "",
    "AppliedType": "",
    "Array": "",
    "ArrayBuffer": "",
    "Attribute": "",
    "Boolean": "",
    "BoxedArray": "",
    "BoxedBooleanArray": "",
    "BoxedByteArray": "",
    "BoxedCharArray": "",
    "Buffer": "",
    "BufferedIterator": "",
    "Byte": "",
    "Char": "",
    "Character": "",
    "Console": "",
    "Double": "",
    "Enumeration": "",
    "Float": "",
    "Fluid": "",
    "Function": "",
    "IScheduler": "",
    "ImmutableMapAdaptor": "",
    "ImmutableSetAdaptor": "",
    "Int": "",
    "Integer": "",
    "Iterable": "",
    "List": "",
    "Long": "",
    "Nil": "",
    "None": "",
    "Option": "",
    "Pair": "",
    "PartialFunction": "",
    "Pid": "",
    "Predef": "",
    "PriorityQueue": "",
    "PriorityQueueProxy": "",
    "Reaction": "",
    "Ref": "",
    "RemoteActor": "",
    "Responder": "",
    "RichInt": "",
    "RichString": "",
    "Rule": "",
    "RuleTransformer": "",
    "SUnit": "",
    "ScalaRunTime": "",
    "Scheduler": "",
    "Script": "",
    "Short": "",
    "Some": "",
    "Stream": "",
    "String": "",
    "Symbol": "",
    "TIMEOUT": "",
    "TcpService": "",
    "TcpServiceWorker": "",
    "TimerThread": "",
    "Unit": "",
    "WorkerThread": "",
    "abstract": "",
    "boolean": "",
    "byte": "",
    "case": "",
    "catch": "",
    "char": "",
    "class": "",
    "def": "",
    "do": "",
    "double": "",
    "else": "",
    "extends": "",
    "false": "",
    "final": "",
    "finally": "",
    "float": "",
    "for": "",
    "forSome": "",
    "if": "",
    "implicit": "",
    "import": "",
    "int": "",
    "lazy": "",
    "long": "",
    "match": "",
    "new": "",
    "null": "",
    "object": "",
    "override": "",
    "package": "",
    "private": "",
    "protected": "",
    "requires": "",
    "return": "",
    "sealed": "",
    "short": "",
    "super": "",
    "this": "",
    "throw": "",
    "trait": "",
    "true": "",
    "try": "",
    "type": "",
    "unit": "",
    "val": "",
    "var": "",
    "while": "",
    "with": "",
    "yield": "",
}

# Keywords dict for scala_pattern ruleset.
scala_pattern_keywords_dict = {}

# Keywords dict for scala_scaladoc ruleset.
scala_scaladoc_keywords_dict = {
#    "\n": "",
#    "    ": "",
#    "      ": "",
    "@access": "",
    "@author": "",
    "@beaninfo": "",
    "@bon": "",
    "@bug": "",
    "@complexity": "",
    "@deprecated": "",
    "@design": "",
    "@docroot": "",
    "@ensures": "",
    "@equivalent": "",
    "@example": "",
    "@exception": "",
    "@generates": "",
    "@guard": "",
    "@hides": "",
    "@history": "",
    "@idea": "",
    "@invariant": "",
    "@link": "",
    "@modifies": "",
    "@overrides": "",
    "@param": "",
    "@post": "",
    "@pre": "",
    "@references": "",
    "@requires": "",
    "@return": "",
    "@review": "",
    "@see": "",
    "@serial": "",
    "@serialData": "",
    "@serialField": "",
    "@serialdata": "",
    "@serialfield": "",
    "@since": "",
    "@spec": "",
    "@throws": "",
    "@todo": "",
    "@uses": "",
    "@values": "",
    "@version": "",
}

# Keywords dict for scala_scaladoc_pre ruleset.
scala_scaladoc_pre_keywords_dict = {}

# Keywords dict for scala_xml_tag ruleset.
scala_xml_tag_keywords_dict = {}

# Keywords dict for scala_xml_text ruleset.
scala_xml_text_keywords_dict = {}

# Keywords dict for scala_xml_comment ruleset.
scala_xml_comment_keywords_dict = {}

# Dictionary of keywords dictionaries for scala mode.
keywordsDictDict = {
    "scala_main": scala_main_keywords_dict,
    "scala_pattern": scala_pattern_keywords_dict,
    "scala_primary": scala_primary_keywords_dict,
    "scala_scaladoc": scala_scaladoc_keywords_dict,
    "scala_scaladoc_pre": scala_scaladoc_pre_keywords_dict,
    "scala_xml_comment": scala_xml_comment_keywords_dict,
    "scala_xml_tag": scala_xml_tag_keywords_dict,
    "scala_xml_text": scala_xml_text_keywords_dict,
}

# Rules for scala_main ruleset.

def scala_rule0(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="label", pattern="@")


# Rules dict for scala_main ruleset.
rulesDict1 = {
    "@": [scala_rule0,],
}

# Rules for scala_primary ruleset.

def scala_rule1(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment1", seq="/**/")

def scala_rule2(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq="//")

def scala_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="comment3", begin="/**", end="*/",
          delegate="scala::scaladoc")

def scala_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def scala_rule5(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="comment2", regexp="<!--",
          at_whitespace_end=True,
          delegate="scala::xml_comment")

def scala_rule6(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp="<\\/?\\w*",
          at_whitespace_end=True,
          delegate="scala::xml_tag")

def scala_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"\"\"", end="\"\"\"")

def scala_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def scala_rule9(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal1", regexp="'([^']|\\\\.)'")

def scala_rule10(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="label", regexp="'[0-9a-zA-Z><=+]([0-9a-zA-Z><=+]|_[0-9a-zA-Z><=+])*")

def scala_rule11(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp="\\[[^\\[\\]]*(\\[[^\\[\\]]*(\\[[^\\[\\]]*\\][^\\[\\]]*)*\\][^\\[\\]]*)*\\]")

def scala_rule12(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp="<:\\s*\\w+(\\.\\w+)*(#\\w+)?")

def scala_rule13(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp=">:\\s*\\w+(\\.\\w+)*(#\\w+)?")

def scala_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def scala_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def scala_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def scala_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def scala_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">:")

def scala_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def scala_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<:")

def scala_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def scala_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def scala_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def scala_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def scala_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def scala_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def scala_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def scala_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def scala_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def scala_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def scala_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="`")

def scala_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def scala_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def scala_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def scala_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=".")

def scala_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=",")

def scala_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=";")

def scala_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="]")

def scala_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="[")

def scala_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="?")

def scala_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq=":")

def scala_rule42(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal2", regexp=":\\s*\\w+(\\.\\w+)*(#\\w+)?")

def scala_rule43(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(")

def scala_rule44(colorer, s, i):
    return colorer.match_span(s, i, kind="", begin="case", end="=>",
          delegate="scala::pattern",
          no_line_break=True)

def scala_rule45(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for scala_primary ruleset.
rulesDict2 = {
    "!": [scala_rule16,],
    "\"": [scala_rule7, scala_rule8,],
    "%": [scala_rule27,],
    "&": [scala_rule28,],
    "'": [scala_rule9, scala_rule10,],
    "(": [scala_rule43,],
    ")": [scala_rule14,],
    "*": [scala_rule24,],
    "+": [scala_rule21,],
    ",": [scala_rule36,],
    "-": [scala_rule22,],
    ".": [scala_rule35,],
    "/": [scala_rule1, scala_rule2, scala_rule3, scala_rule4, scala_rule23,],
    "0": [scala_rule45,],
    "1": [scala_rule45,],
    "2": [scala_rule45,],
    "3": [scala_rule45,],
    "4": [scala_rule45,],
    "5": [scala_rule45,],
    "6": [scala_rule45,],
    "7": [scala_rule45,],
    "8": [scala_rule45,],
    "9": [scala_rule45,],
    ":": [scala_rule41, scala_rule42,],
    ";": [scala_rule37,],
    "<": [scala_rule5, scala_rule6, scala_rule12, scala_rule19, scala_rule20, scala_rule26,],
    "=": [scala_rule15, scala_rule45,],
    ">": [scala_rule13, scala_rule17, scala_rule18, scala_rule25, scala_rule45,],
    "?": [scala_rule40,],
    "@": [scala_rule45,],
    "A": [scala_rule45,],
    "B": [scala_rule45,],
    "C": [scala_rule45,],
    "D": [scala_rule45,],
    "E": [scala_rule45,],
    "F": [scala_rule45,],
    "G": [scala_rule45,],
    "H": [scala_rule45,],
    "I": [scala_rule45,],
    "J": [scala_rule45,],
    "K": [scala_rule45,],
    "L": [scala_rule45,],
    "M": [scala_rule45,],
    "N": [scala_rule45,],
    "O": [scala_rule45,],
    "P": [scala_rule45,],
    "Q": [scala_rule45,],
    "R": [scala_rule45,],
    "S": [scala_rule45,],
    "T": [scala_rule45,],
    "U": [scala_rule45,],
    "V": [scala_rule45,],
    "W": [scala_rule45,],
    "X": [scala_rule45,],
    "Y": [scala_rule45,],
    "Z": [scala_rule45,],
    "[": [scala_rule11, scala_rule39,],
    "]": [scala_rule38,],
    "^": [scala_rule30,],
    "`": [scala_rule31,],
    "a": [scala_rule45,],
    "b": [scala_rule45,],
    "c": [scala_rule44, scala_rule45,],
    "d": [scala_rule45,],
    "e": [scala_rule45,],
    "f": [scala_rule45,],
    "g": [scala_rule45,],
    "h": [scala_rule45,],
    "i": [scala_rule45,],
    "j": [scala_rule45,],
    "k": [scala_rule45,],
    "l": [scala_rule45,],
    "m": [scala_rule45,],
    "n": [scala_rule45,],
    "o": [scala_rule45,],
    "p": [scala_rule45,],
    "q": [scala_rule45,],
    "r": [scala_rule45,],
    "s": [scala_rule45,],
    "t": [scala_rule45,],
    "u": [scala_rule45,],
    "v": [scala_rule45,],
    "w": [scala_rule45,],
    "x": [scala_rule45,],
    "y": [scala_rule45,],
    "z": [scala_rule45,],
    "{": [scala_rule34,],
    "|": [scala_rule29,],
    "}": [scala_rule33,],
    "~": [scala_rule32,],
}

# Rules for scala_pattern ruleset.


def scala_rule46(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

# Rules dict for scala_pattern ruleset.
rulesDict3 = {
    "@": [scala_rule46,],
}

# Rules for scala_scaladoc ruleset.

def scala_rule47(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="{")

def scala_rule48(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="*")

def scala_rule49(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<pre>", end="</pre>",
          delegate="scala::scaladoc_pre")

def scala_rule50(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def scala_rule51(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="<<")

def scala_rule52(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="<=")

def scala_rule53(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="comment3", seq="< ")

def scala_rule54(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="xml::tags")

def scala_rule55(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for scala_scaladoc ruleset.
rulesDict4 = {
    "*": [scala_rule48,],
    "0": [scala_rule55,],
    "1": [scala_rule55,],
    "2": [scala_rule55,],
    "3": [scala_rule55,],
    "4": [scala_rule55,],
    "5": [scala_rule55,],
    "6": [scala_rule55,],
    "7": [scala_rule55,],
    "8": [scala_rule55,],
    "9": [scala_rule55,],
    "<": [scala_rule49, scala_rule50, scala_rule51, scala_rule52, scala_rule53, scala_rule54,],
    "=": [scala_rule55,],
    ">": [scala_rule55,],
    "@": [scala_rule55,],
    "A": [scala_rule55,],
    "B": [scala_rule55,],
    "C": [scala_rule55,],
    "D": [scala_rule55,],
    "E": [scala_rule55,],
    "F": [scala_rule55,],
    "G": [scala_rule55,],
    "H": [scala_rule55,],
    "I": [scala_rule55,],
    "J": [scala_rule55,],
    "K": [scala_rule55,],
    "L": [scala_rule55,],
    "M": [scala_rule55,],
    "N": [scala_rule55,],
    "O": [scala_rule55,],
    "P": [scala_rule55,],
    "Q": [scala_rule55,],
    "R": [scala_rule55,],
    "S": [scala_rule55,],
    "T": [scala_rule55,],
    "U": [scala_rule55,],
    "V": [scala_rule55,],
    "W": [scala_rule55,],
    "X": [scala_rule55,],
    "Y": [scala_rule55,],
    "Z": [scala_rule55,],
    "a": [scala_rule55,],
    "b": [scala_rule55,],
    "c": [scala_rule55,],
    "d": [scala_rule55,],
    "e": [scala_rule55,],
    "f": [scala_rule55,],
    "g": [scala_rule55,],
    "h": [scala_rule55,],
    "i": [scala_rule55,],
    "j": [scala_rule55,],
    "k": [scala_rule55,],
    "l": [scala_rule55,],
    "m": [scala_rule55,],
    "n": [scala_rule55,],
    "o": [scala_rule55,],
    "p": [scala_rule55,],
    "q": [scala_rule55,],
    "r": [scala_rule55,],
    "s": [scala_rule55,],
    "t": [scala_rule55,],
    "u": [scala_rule55,],
    "v": [scala_rule55,],
    "w": [scala_rule55,],
    "x": [scala_rule55,],
    "y": [scala_rule55,],
    "z": [scala_rule55,],
    "{": [scala_rule47,],
}

# Rules for scala_scaladoc_pre ruleset.

# Rules dict for scala_scaladoc_pre ruleset.
rulesDict5 = {}

# Rules for scala_xml_tag ruleset.

def scala_rule56(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def scala_rule57(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def scala_rule58(colorer, s, i):
    return colorer.match_span(s, i, kind="", begin="{", end="}",
          delegate="scala::main")

def scala_rule59(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp=">$",
          delegate="scala::main")

def scala_rule60(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp=">\\s*;",
          delegate="scala::main")

def scala_rule61(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp=">\\s*\\)",
          delegate="scala::main")

def scala_rule62(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal3", seq=">",
          delegate="scala::xml_text")

# Rules dict for scala_xml_tag ruleset.
rulesDict6 = {
    "\"": [scala_rule56,],
    "'": [scala_rule57,],
    ">": [scala_rule59, scala_rule60, scala_rule61, scala_rule62,],
    "{": [scala_rule58,],
}

# Rules for scala_xml_text ruleset.

def scala_rule63(colorer, s, i):
    return colorer.match_span(s, i, kind="", begin="{", end="}",
          delegate="scala::main")

def scala_rule64(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="comment2", regexp="<!--",
          delegate="scala::xml_comment")

def scala_rule65(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="literal3", regexp="<\\/?\\w*",
          delegate="scala::xml_tag")

# Rules dict for scala_xml_text ruleset.
rulesDict7 = {
    "<": [scala_rule64, scala_rule65,],
    "{": [scala_rule63,],
}

# Rules for scala_xml_comment ruleset.

def scala_rule66(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="comment2", regexp="-->$",
          delegate="scala::main")

def scala_rule67(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="comment2", regexp="-->\\s*;",
          delegate="scala::main")

def scala_rule68(colorer, s, i):
    return colorer.match_seq(s, i, kind="comment2", seq="-->",
          delegate="scala::xml_text")

# Rules dict for scala_xml_comment ruleset.
rulesDict8 = {
    "-": [scala_rule66, scala_rule67, scala_rule68,],
}

# x.rulesDictDict for scala mode.
rulesDictDict = {
    "scala_main": rulesDict1,
    "scala_pattern": rulesDict3,
    "scala_primary": rulesDict2,
    "scala_scaladoc": rulesDict4,
    "scala_scaladoc_pre": rulesDict5,
    "scala_xml_comment": rulesDict8,
    "scala_xml_tag": rulesDict6,
    "scala_xml_text": rulesDict7,
}

# Import dict for scala mode.
importDict = {
    "scala_main": ["scala_main::primary",],
    "scala_pattern": ["scala_pattern::primary",],
}
