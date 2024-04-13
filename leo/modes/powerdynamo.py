# Leo colorizer control file for powerdynamo mode.
# This file is in the public domain.

# Properties for powerdynamo mode.
properties = {
    "commentEnd": "-->",
    "commentStart": "<!--",
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "//",
    "lineUpClosingBracket": "true",
    "wordBreakChars": " @ %^*()+=|\\{}[]:;,.?$&",
}

# Attributes dict for powerdynamo_main ruleset.
powerdynamo_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for powerdynamo_tags ruleset.
powerdynamo_tags_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for powerdynamo_tags_literal ruleset.
powerdynamo_tags_literal_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for powerdynamo_powerdynamo_script ruleset.
powerdynamo_powerdynamo_script_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for powerdynamo_powerdynamo_tag_general ruleset.
powerdynamo_powerdynamo_tag_general_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for powerdynamo_powerdynamo_tag_data ruleset.
powerdynamo_powerdynamo_tag_data_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Attributes dict for powerdynamo_powerdynamo_tag_document ruleset.
powerdynamo_powerdynamo_tag_document_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for powerdynamo mode.
attributesDictDict = {
    "powerdynamo_main": powerdynamo_main_attributes_dict,
    "powerdynamo_powerdynamo_script": powerdynamo_powerdynamo_script_attributes_dict,
    "powerdynamo_powerdynamo_tag_data": powerdynamo_powerdynamo_tag_data_attributes_dict,
    "powerdynamo_powerdynamo_tag_document": powerdynamo_powerdynamo_tag_document_attributes_dict,
    "powerdynamo_powerdynamo_tag_general": powerdynamo_powerdynamo_tag_general_attributes_dict,
    "powerdynamo_tags": powerdynamo_tags_attributes_dict,
    "powerdynamo_tags_literal": powerdynamo_tags_literal_attributes_dict,
}

# Keywords dict for powerdynamo_main ruleset.
powerdynamo_main_keywords_dict = {}

# Keywords dict for powerdynamo_tags ruleset.
powerdynamo_tags_keywords_dict = {}

# Keywords dict for powerdynamo_tags_literal ruleset.
powerdynamo_tags_literal_keywords_dict = {}

# Keywords dict for powerdynamo_powerdynamo_script ruleset.
powerdynamo_powerdynamo_script_keywords_dict = {
    "abstract": "keyword1",
    "askquestion": "keyword3",
    "autocommit": "keyword3",
    "boolean": "keyword1",
    "break": "keyword1",
    "byte": "keyword1",
    "cachedoutputtimeout": "keyword3",
    "case": "keyword1",
    "catch": "keyword1",
    "char": "keyword1",
    "charat": "keyword3",
    "class": "keyword1",
    "close": "keyword3",
    "commit": "keyword3",
    "connect": "keyword3",
    "connected": "keyword3",
    "connection": "keyword3",
    "connectionid": "keyword3",
    "connectionname": "keyword3",
    "connectiontype": "keyword3",
    "connectparameters": "keyword3",
    "contenttype": "keyword3",
    "continue": "keyword1",
    "createconnection": "keyword3",
    "createdocument": "keyword3",
    "createpropertysheet": "keyword3",
    "createquery": "keyword3",
    "createwizard": "keyword3",
    "database": "keyword3",
    "datasource": "keyword3",
    "datasourcelist": "keyword3",
    "default": "keyword1",
    "deleteconnection": "keyword3",
    "deletedocument": "keyword3",
    "description": "keyword3",
    "disconnect": "keyword3",
    "do": "keyword1",
    "document": "keyword2",
    "double": "keyword1",
    "else": "keyword1",
    "eof": "keyword3",
    "errornumber": "keyword3",
    "errorstring": "keyword3",
    "exec": "keyword3",
    "execute": "keyword3",
    "exists": "keyword1",
    "exportto": "keyword3",
    "extends": "keyword1",
    "false": "keyword1",
    "file": "keyword2",
    "final": "keyword1",
    "finally": "keyword1",
    "float": "keyword1",
    "for": "keyword1",
    "function": "keyword1",
    "getcolumncount": "keyword3",
    "getcolumnindex": "keyword3",
    "getcolumnlabel": "keyword3",
    "getconnection": "keyword3",
    "getconnectionidlist": "keyword3",
    "getconnectionnamelist": "keyword3",
    "getcwd": "keyword3",
    "getdirectory": "keyword3",
    "getdocument": "keyword3",
    "getempty": "keyword3",
    "getenv": "keyword3",
    "geterrorcode": "keyword3",
    "geterrorinfo": "keyword3",
    "geteventlist": "keyword3",
    "getfileptr": "keyword3",
    "getgenerated": "keyword3",
    "getrootdocument": "keyword3",
    "getrowcount": "keyword3",
    "getservervariable": "keyword3",
    "getstate": "keyword3",
    "getsupportedmoves": "keyword3",
    "getvalue": "keyword3",
    "id": "keyword3",
    "if": "keyword1",
    "implements": "keyword1",
    "import": "keyword1",
    "importfrom": "keyword3",
    "include": "keyword3",
    "indexof": "keyword3",
    "instanceof": "keyword1",
    "int": "keyword1",
    "interface": "keyword1",
    "lastindexof": "keyword3",
    "lastmodified": "keyword3",
    "length": "keyword3",
    "location": "keyword3",
    "long": "keyword1",
    "mode": "keyword3",
    "move": "keyword3",
    "movefirst": "keyword3",
    "movelast": "keyword3",
    "movenext": "keyword3",
    "moveprevious": "keyword3",
    "moverelative": "keyword3",
    "name": "keyword3",
    "native": "keyword1",
    "new": "keyword1",
    "null": "keyword1",
    "onevent": "keyword3",
    "open": "keyword3",
    "opened": "keyword3",
    "package": "keyword1",
    "parent": "keyword3",
    "password": "keyword3",
    "private": "keyword1",
    "protected": "keyword1",
    "public": "keyword1",
    "query": "keyword2",
    "readchar": "keyword3",
    "readline": "keyword3",
    "redirect": "keyword3",
    "refresh": "keyword3",
    "return": "keyword1",
    "rollback": "keyword3",
    "seek": "keyword3",
    "server": "keyword3",
    "session": "keyword2",
    "setenv": "keyword3",
    "setsql": "keyword3",
    "short": "keyword1",
    "showmessage": "keyword3",
    "simulatecursors": "keyword3",
    "site": "keyword2",
    "size": "keyword3",
    "source": "keyword3",
    "static": "keyword1",
    "status": "keyword3",
    "substring": "keyword3",
    "super": "keyword1",
    "switch": "keyword1",
    "synchronized": "keyword1",
    "system": "keyword2",
    "this": "keyword1",
    "threadsafe": "keyword1",
    "throw": "keyword1",
    "throws": "keyword1",
    "timeout": "keyword3",
    "tolowercase": "keyword3",
    "touppercase": "keyword3",
    "transient": "keyword1",
    "true": "keyword1",
    "try": "keyword1",
    "type": "keyword3",
    "typeof": "keyword2",
    "userid": "keyword3",
    "value": "keyword3",
    "var": "keyword1",
    "void": "keyword1",
    "while": "keyword1",
    "write": "keyword3",
    "writeline": "keyword3",
    "writeln": "keyword3",
}

# Keywords dict for powerdynamo_powerdynamo_tag_general ruleset.
powerdynamo_powerdynamo_tag_general_keywords_dict = {
    "name": "keyword2",
}

# Keywords dict for powerdynamo_powerdynamo_tag_data ruleset.
powerdynamo_powerdynamo_tag_data_keywords_dict = {
    "name": "keyword2",
    "query": "keyword2",
}

# Keywords dict for powerdynamo_powerdynamo_tag_document ruleset.
powerdynamo_powerdynamo_tag_document_keywords_dict = {
    "cached_output_timeout": "keyword2",
    "content_type": "keyword2",
    "redirect": "keyword2",
    "status": "keyword2",
}

# Dictionary of keywords dictionaries for powerdynamo mode.
keywordsDictDict = {
    "powerdynamo_main": powerdynamo_main_keywords_dict,
    "powerdynamo_powerdynamo_script": powerdynamo_powerdynamo_script_keywords_dict,
    "powerdynamo_powerdynamo_tag_data": powerdynamo_powerdynamo_tag_data_keywords_dict,
    "powerdynamo_powerdynamo_tag_document": powerdynamo_powerdynamo_tag_document_keywords_dict,
    "powerdynamo_powerdynamo_tag_general": powerdynamo_powerdynamo_tag_general_keywords_dict,
    "powerdynamo_tags": powerdynamo_tags_keywords_dict,
    "powerdynamo_tags_literal": powerdynamo_tags_literal_keywords_dict,
}

# Rules for powerdynamo_main ruleset.

def powerdynamo_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--script", end="-->",
          delegate="powerdynamo::powerdynamo-script")

def powerdynamo_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--data", end="-->",
          delegate="powerdynamo::powerdynamo-tag-data")

def powerdynamo_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--document", end="-->",
          delegate="powerdynamo::powerdynamo-tag-document")

def powerdynamo_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--evaluate", end="-->",
          delegate="powerdynamo::powerdynamo-script")

def powerdynamo_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--execute", end="-->",
          delegate="powerdynamo::powerdynamo-script")

def powerdynamo_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--formatting", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--/formatting", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--include", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--label", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--sql", end="-->",
          delegate="transact-sql::main")

def powerdynamo_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--sql_error_code", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--sql_error_info", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--sql_state", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule13(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--sql_on_no_error", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule14(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--/sql_on_no_error", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--sql_on_error", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule16(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--/sql_on_error", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule17(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--sql_on_no_rows", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule18(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--/sql_on_no_rows", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule19(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--sql_on_rows", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule20(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--/sql_on_rows", end="-->",
          delegate="powerdynamo::powerdynamo-tag-general")

def powerdynamo_rule21(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->")

def powerdynamo_rule22(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<SCRIPT", end="</SCRIPT>",
          delegate="html::javascript")

def powerdynamo_rule23(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<STYLE", end="</STYLE>",
          delegate="html::css")

def powerdynamo_rule24(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="<!", end=">",
          delegate="xml::dtd-tags")

def powerdynamo_rule25(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
          delegate="powerdynamo::tags")

def powerdynamo_rule26(colorer, s, i):
    return colorer.match_span(s, i, kind="literal2", begin="&", end=";",
          no_word_break=True)

# Rules dict for powerdynamo_main ruleset.
rulesDict1 = {
    "&": [powerdynamo_rule26,],
    "<": [powerdynamo_rule0, powerdynamo_rule1, powerdynamo_rule2, powerdynamo_rule3, powerdynamo_rule4, powerdynamo_rule5, powerdynamo_rule6, powerdynamo_rule7, powerdynamo_rule8, powerdynamo_rule9, powerdynamo_rule10, powerdynamo_rule11, powerdynamo_rule12, powerdynamo_rule13, powerdynamo_rule14, powerdynamo_rule15, powerdynamo_rule16, powerdynamo_rule17, powerdynamo_rule18, powerdynamo_rule19, powerdynamo_rule20, powerdynamo_rule21, powerdynamo_rule22, powerdynamo_rule23, powerdynamo_rule24, powerdynamo_rule25,],
}

# Rules for powerdynamo_tags ruleset.

def powerdynamo_rule27(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--script", end="--?>",
          delegate="powerdynamo::powerdynamo-script")

def powerdynamo_rule28(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="powerdynamo::tags_literal")

def powerdynamo_rule29(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="powerdynamo::tags_literal")

def powerdynamo_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

# Rules dict for powerdynamo_tags ruleset.
rulesDict2 = {
    "\"": [powerdynamo_rule28,],
    "'": [powerdynamo_rule29,],
    "<": [powerdynamo_rule27,],
    "=": [powerdynamo_rule30,],
}

# Rules for powerdynamo_tags_literal ruleset.

def powerdynamo_rule31(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="<!--script", end="?-->",
          delegate="powerdynamo::powerdynamo-script")

# Rules dict for powerdynamo_tags_literal ruleset.
rulesDict3 = {
    "<": [powerdynamo_rule31,],
}

# Rules for powerdynamo_powerdynamo_script ruleset.

def powerdynamo_rule32(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def powerdynamo_rule33(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="powerdynamo::powerdynamo_literal")

def powerdynamo_rule34(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="powerdynamo::powerdynamo_literal")

def powerdynamo_rule35(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="//")

def powerdynamo_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def powerdynamo_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def powerdynamo_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def powerdynamo_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def powerdynamo_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def powerdynamo_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def powerdynamo_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def powerdynamo_rule43(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def powerdynamo_rule44(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def powerdynamo_rule45(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def powerdynamo_rule46(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def powerdynamo_rule47(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def powerdynamo_rule48(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def powerdynamo_rule49(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def powerdynamo_rule50(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def powerdynamo_rule51(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def powerdynamo_rule52(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".")

def powerdynamo_rule53(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def powerdynamo_rule54(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def powerdynamo_rule55(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=",")

def powerdynamo_rule56(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=";")

def powerdynamo_rule57(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="]")

def powerdynamo_rule58(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="[")

def powerdynamo_rule59(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def powerdynamo_rule60(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="@")

def powerdynamo_rule61(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def powerdynamo_rule62(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="function", pattern="(",
          exclude_match=True)

def powerdynamo_rule63(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for powerdynamo_powerdynamo_script ruleset.
rulesDict4 = {
    "!": [powerdynamo_rule37,],
    "\"": [powerdynamo_rule33,],
    "%": [powerdynamo_rule47,],
    "&": [powerdynamo_rule48,],
    "'": [powerdynamo_rule34,],
    "(": [powerdynamo_rule62,],
    "*": [powerdynamo_rule44,],
    "+": [powerdynamo_rule41,],
    ",": [powerdynamo_rule55,],
    "-": [powerdynamo_rule42,],
    ".": [powerdynamo_rule52,],
    "/": [powerdynamo_rule32, powerdynamo_rule35, powerdynamo_rule43,],
    "0": [powerdynamo_rule63,],
    "1": [powerdynamo_rule63,],
    "2": [powerdynamo_rule63,],
    "3": [powerdynamo_rule63,],
    "4": [powerdynamo_rule63,],
    "5": [powerdynamo_rule63,],
    "6": [powerdynamo_rule63,],
    "7": [powerdynamo_rule63,],
    "8": [powerdynamo_rule63,],
    "9": [powerdynamo_rule63,],
    ":": [powerdynamo_rule61,],
    ";": [powerdynamo_rule56,],
    "<": [powerdynamo_rule39, powerdynamo_rule46,],
    "=": [powerdynamo_rule36, powerdynamo_rule40,],
    ">": [powerdynamo_rule38, powerdynamo_rule45,],
    "?": [powerdynamo_rule59,],
    "@": [powerdynamo_rule60, powerdynamo_rule63,],
    "A": [powerdynamo_rule63,],
    "B": [powerdynamo_rule63,],
    "C": [powerdynamo_rule63,],
    "D": [powerdynamo_rule63,],
    "E": [powerdynamo_rule63,],
    "F": [powerdynamo_rule63,],
    "G": [powerdynamo_rule63,],
    "H": [powerdynamo_rule63,],
    "I": [powerdynamo_rule63,],
    "J": [powerdynamo_rule63,],
    "K": [powerdynamo_rule63,],
    "L": [powerdynamo_rule63,],
    "M": [powerdynamo_rule63,],
    "N": [powerdynamo_rule63,],
    "O": [powerdynamo_rule63,],
    "P": [powerdynamo_rule63,],
    "Q": [powerdynamo_rule63,],
    "R": [powerdynamo_rule63,],
    "S": [powerdynamo_rule63,],
    "T": [powerdynamo_rule63,],
    "U": [powerdynamo_rule63,],
    "V": [powerdynamo_rule63,],
    "W": [powerdynamo_rule63,],
    "X": [powerdynamo_rule63,],
    "Y": [powerdynamo_rule63,],
    "Z": [powerdynamo_rule63,],
    "[": [powerdynamo_rule58,],
    "]": [powerdynamo_rule57,],
    "^": [powerdynamo_rule50,],
    "_": [powerdynamo_rule63,],
    "a": [powerdynamo_rule63,],
    "b": [powerdynamo_rule63,],
    "c": [powerdynamo_rule63,],
    "d": [powerdynamo_rule63,],
    "e": [powerdynamo_rule63,],
    "f": [powerdynamo_rule63,],
    "g": [powerdynamo_rule63,],
    "h": [powerdynamo_rule63,],
    "i": [powerdynamo_rule63,],
    "j": [powerdynamo_rule63,],
    "k": [powerdynamo_rule63,],
    "l": [powerdynamo_rule63,],
    "m": [powerdynamo_rule63,],
    "n": [powerdynamo_rule63,],
    "o": [powerdynamo_rule63,],
    "p": [powerdynamo_rule63,],
    "q": [powerdynamo_rule63,],
    "r": [powerdynamo_rule63,],
    "s": [powerdynamo_rule63,],
    "t": [powerdynamo_rule63,],
    "u": [powerdynamo_rule63,],
    "v": [powerdynamo_rule63,],
    "w": [powerdynamo_rule63,],
    "x": [powerdynamo_rule63,],
    "y": [powerdynamo_rule63,],
    "z": [powerdynamo_rule63,],
    "{": [powerdynamo_rule54,],
    "|": [powerdynamo_rule49,],
    "}": [powerdynamo_rule53,],
    "~": [powerdynamo_rule51,],
}

# Rules for powerdynamo_powerdynamo_tag_general ruleset.

def powerdynamo_rule64(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="powerdynamo::powerdynamo_literal")

def powerdynamo_rule65(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="powerdynamo::powerdynamo_literal")

def powerdynamo_rule66(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for powerdynamo_powerdynamo_tag_general ruleset.
rulesDict5 = {
    "\"": [powerdynamo_rule64,],
    "'": [powerdynamo_rule65,],
    "0": [powerdynamo_rule66,],
    "1": [powerdynamo_rule66,],
    "2": [powerdynamo_rule66,],
    "3": [powerdynamo_rule66,],
    "4": [powerdynamo_rule66,],
    "5": [powerdynamo_rule66,],
    "6": [powerdynamo_rule66,],
    "7": [powerdynamo_rule66,],
    "8": [powerdynamo_rule66,],
    "9": [powerdynamo_rule66,],
    "@": [powerdynamo_rule66,],
    "A": [powerdynamo_rule66,],
    "B": [powerdynamo_rule66,],
    "C": [powerdynamo_rule66,],
    "D": [powerdynamo_rule66,],
    "E": [powerdynamo_rule66,],
    "F": [powerdynamo_rule66,],
    "G": [powerdynamo_rule66,],
    "H": [powerdynamo_rule66,],
    "I": [powerdynamo_rule66,],
    "J": [powerdynamo_rule66,],
    "K": [powerdynamo_rule66,],
    "L": [powerdynamo_rule66,],
    "M": [powerdynamo_rule66,],
    "N": [powerdynamo_rule66,],
    "O": [powerdynamo_rule66,],
    "P": [powerdynamo_rule66,],
    "Q": [powerdynamo_rule66,],
    "R": [powerdynamo_rule66,],
    "S": [powerdynamo_rule66,],
    "T": [powerdynamo_rule66,],
    "U": [powerdynamo_rule66,],
    "V": [powerdynamo_rule66,],
    "W": [powerdynamo_rule66,],
    "X": [powerdynamo_rule66,],
    "Y": [powerdynamo_rule66,],
    "Z": [powerdynamo_rule66,],
    "_": [powerdynamo_rule66,],
    "a": [powerdynamo_rule66,],
    "b": [powerdynamo_rule66,],
    "c": [powerdynamo_rule66,],
    "d": [powerdynamo_rule66,],
    "e": [powerdynamo_rule66,],
    "f": [powerdynamo_rule66,],
    "g": [powerdynamo_rule66,],
    "h": [powerdynamo_rule66,],
    "i": [powerdynamo_rule66,],
    "j": [powerdynamo_rule66,],
    "k": [powerdynamo_rule66,],
    "l": [powerdynamo_rule66,],
    "m": [powerdynamo_rule66,],
    "n": [powerdynamo_rule66,],
    "o": [powerdynamo_rule66,],
    "p": [powerdynamo_rule66,],
    "q": [powerdynamo_rule66,],
    "r": [powerdynamo_rule66,],
    "s": [powerdynamo_rule66,],
    "t": [powerdynamo_rule66,],
    "u": [powerdynamo_rule66,],
    "v": [powerdynamo_rule66,],
    "w": [powerdynamo_rule66,],
    "x": [powerdynamo_rule66,],
    "y": [powerdynamo_rule66,],
    "z": [powerdynamo_rule66,],
}

# Rules for powerdynamo_powerdynamo_tag_data ruleset.

def powerdynamo_rule67(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="powerdynamo::powerdynamo_literal")

def powerdynamo_rule68(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="powerdynamo::powerdynamo_literal")

def powerdynamo_rule69(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for powerdynamo_powerdynamo_tag_data ruleset.
rulesDict6 = {
    "\"": [powerdynamo_rule67,],
    "'": [powerdynamo_rule68,],
    "0": [powerdynamo_rule69,],
    "1": [powerdynamo_rule69,],
    "2": [powerdynamo_rule69,],
    "3": [powerdynamo_rule69,],
    "4": [powerdynamo_rule69,],
    "5": [powerdynamo_rule69,],
    "6": [powerdynamo_rule69,],
    "7": [powerdynamo_rule69,],
    "8": [powerdynamo_rule69,],
    "9": [powerdynamo_rule69,],
    "@": [powerdynamo_rule69,],
    "A": [powerdynamo_rule69,],
    "B": [powerdynamo_rule69,],
    "C": [powerdynamo_rule69,],
    "D": [powerdynamo_rule69,],
    "E": [powerdynamo_rule69,],
    "F": [powerdynamo_rule69,],
    "G": [powerdynamo_rule69,],
    "H": [powerdynamo_rule69,],
    "I": [powerdynamo_rule69,],
    "J": [powerdynamo_rule69,],
    "K": [powerdynamo_rule69,],
    "L": [powerdynamo_rule69,],
    "M": [powerdynamo_rule69,],
    "N": [powerdynamo_rule69,],
    "O": [powerdynamo_rule69,],
    "P": [powerdynamo_rule69,],
    "Q": [powerdynamo_rule69,],
    "R": [powerdynamo_rule69,],
    "S": [powerdynamo_rule69,],
    "T": [powerdynamo_rule69,],
    "U": [powerdynamo_rule69,],
    "V": [powerdynamo_rule69,],
    "W": [powerdynamo_rule69,],
    "X": [powerdynamo_rule69,],
    "Y": [powerdynamo_rule69,],
    "Z": [powerdynamo_rule69,],
    "_": [powerdynamo_rule69,],
    "a": [powerdynamo_rule69,],
    "b": [powerdynamo_rule69,],
    "c": [powerdynamo_rule69,],
    "d": [powerdynamo_rule69,],
    "e": [powerdynamo_rule69,],
    "f": [powerdynamo_rule69,],
    "g": [powerdynamo_rule69,],
    "h": [powerdynamo_rule69,],
    "i": [powerdynamo_rule69,],
    "j": [powerdynamo_rule69,],
    "k": [powerdynamo_rule69,],
    "l": [powerdynamo_rule69,],
    "m": [powerdynamo_rule69,],
    "n": [powerdynamo_rule69,],
    "o": [powerdynamo_rule69,],
    "p": [powerdynamo_rule69,],
    "q": [powerdynamo_rule69,],
    "r": [powerdynamo_rule69,],
    "s": [powerdynamo_rule69,],
    "t": [powerdynamo_rule69,],
    "u": [powerdynamo_rule69,],
    "v": [powerdynamo_rule69,],
    "w": [powerdynamo_rule69,],
    "x": [powerdynamo_rule69,],
    "y": [powerdynamo_rule69,],
    "z": [powerdynamo_rule69,],
}

# Rules for powerdynamo_powerdynamo_tag_document ruleset.

def powerdynamo_rule70(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          delegate="powerdynamo::powerdynamo_literal")

def powerdynamo_rule71(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          delegate="powerdynamo::powerdynamo_literal")

def powerdynamo_rule72(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for powerdynamo_powerdynamo_tag_document ruleset.
rulesDict7 = {
    "\"": [powerdynamo_rule70,],
    "'": [powerdynamo_rule71,],
    "0": [powerdynamo_rule72,],
    "1": [powerdynamo_rule72,],
    "2": [powerdynamo_rule72,],
    "3": [powerdynamo_rule72,],
    "4": [powerdynamo_rule72,],
    "5": [powerdynamo_rule72,],
    "6": [powerdynamo_rule72,],
    "7": [powerdynamo_rule72,],
    "8": [powerdynamo_rule72,],
    "9": [powerdynamo_rule72,],
    "@": [powerdynamo_rule72,],
    "A": [powerdynamo_rule72,],
    "B": [powerdynamo_rule72,],
    "C": [powerdynamo_rule72,],
    "D": [powerdynamo_rule72,],
    "E": [powerdynamo_rule72,],
    "F": [powerdynamo_rule72,],
    "G": [powerdynamo_rule72,],
    "H": [powerdynamo_rule72,],
    "I": [powerdynamo_rule72,],
    "J": [powerdynamo_rule72,],
    "K": [powerdynamo_rule72,],
    "L": [powerdynamo_rule72,],
    "M": [powerdynamo_rule72,],
    "N": [powerdynamo_rule72,],
    "O": [powerdynamo_rule72,],
    "P": [powerdynamo_rule72,],
    "Q": [powerdynamo_rule72,],
    "R": [powerdynamo_rule72,],
    "S": [powerdynamo_rule72,],
    "T": [powerdynamo_rule72,],
    "U": [powerdynamo_rule72,],
    "V": [powerdynamo_rule72,],
    "W": [powerdynamo_rule72,],
    "X": [powerdynamo_rule72,],
    "Y": [powerdynamo_rule72,],
    "Z": [powerdynamo_rule72,],
    "_": [powerdynamo_rule72,],
    "a": [powerdynamo_rule72,],
    "b": [powerdynamo_rule72,],
    "c": [powerdynamo_rule72,],
    "d": [powerdynamo_rule72,],
    "e": [powerdynamo_rule72,],
    "f": [powerdynamo_rule72,],
    "g": [powerdynamo_rule72,],
    "h": [powerdynamo_rule72,],
    "i": [powerdynamo_rule72,],
    "j": [powerdynamo_rule72,],
    "k": [powerdynamo_rule72,],
    "l": [powerdynamo_rule72,],
    "m": [powerdynamo_rule72,],
    "n": [powerdynamo_rule72,],
    "o": [powerdynamo_rule72,],
    "p": [powerdynamo_rule72,],
    "q": [powerdynamo_rule72,],
    "r": [powerdynamo_rule72,],
    "s": [powerdynamo_rule72,],
    "t": [powerdynamo_rule72,],
    "u": [powerdynamo_rule72,],
    "v": [powerdynamo_rule72,],
    "w": [powerdynamo_rule72,],
    "x": [powerdynamo_rule72,],
    "y": [powerdynamo_rule72,],
    "z": [powerdynamo_rule72,],
}

# x.rulesDictDict for powerdynamo mode.
rulesDictDict = {
    "powerdynamo_main": rulesDict1,
    "powerdynamo_powerdynamo_script": rulesDict4,
    "powerdynamo_powerdynamo_tag_data": rulesDict6,
    "powerdynamo_powerdynamo_tag_document": rulesDict7,
    "powerdynamo_powerdynamo_tag_general": rulesDict5,
    "powerdynamo_tags": rulesDict2,
    "powerdynamo_tags_literal": rulesDict3,
}

# Import dict for powerdynamo mode.
importDict = {}
