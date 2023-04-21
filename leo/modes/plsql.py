# Leo colorizer control file for plsql mode.
# This file is in the public domain.

# Properties for plsql mode.
properties = {
    "commentEnd": "*/",
    "commentStart": "/*",
    "lineComment": "--",
}

# Attributes dict for plsql_main ruleset.
plsql_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for plsql mode.
attributesDictDict = {
    "plsql_main": plsql_main_attributes_dict,
}

# Keywords dict for plsql_main ruleset.
plsql_main_keywords_dict = {
    "abort": "keyword1",
    "abs": "keyword2",
    "access": "keyword1",
    "acos": "keyword2",
    "add": "keyword1",
    "add_months": "keyword2",
    "all": "keyword1",
    "alter": "keyword1",
    "and": "keyword1",
    "any": "keyword1",
    "array": "keyword1",
    "array_len": "keyword1",
    "arraysize": "keyword3",
    "as": "keyword1",
    "asc": "keyword1",
    "ascii": "keyword2",
    "asin": "keyword2",
    "assert": "keyword1",
    "assign": "keyword1",
    "at": "keyword1",
    "atan": "keyword2",
    "atan2": "keyword2",
    "audit": "keyword1",
    "authorization": "keyword1",
    "avg": "keyword1",
    "base_table": "keyword1",
    "begin": "keyword1",
    "between": "keyword1",
    "binary": "keyword1",
    "binary_integer": "keyword1",
    "bit": "keyword1",
    "blob": "keyword1",
    "body": "keyword1",
    "boolean": "keyword1",
    "by": "keyword1",
    "case": "keyword1",
    "ceil": "keyword2",
    "char": "keyword1",
    "char_base": "keyword1",
    "character": "keyword1",
    "chartorowid": "keyword2",
    "check": "keyword1",
    "chr": "keyword2",
    "close": "keyword1",
    "cluster": "keyword1",
    "clusters": "keyword1",
    "colauth": "keyword1",
    "column": "keyword1",
    "comment": "keyword1",
    "commit": "keyword1",
    "compress": "keyword1",
    "concat": "keyword2",
    "connect": "keyword1",
    "constant": "keyword1",
    "constraint": "keyword1",
    "convert": "keyword2",
    "cos": "keyword2",
    "cosh": "keyword2",
    "count": "keyword1",
    "create": "keyword1",
    "current": "keyword1",
    "currval": "keyword1",
    "cursor": "keyword1",
    "data_base": "keyword1",
    "database": "keyword1",
    "date": "keyword1",
    "datetime": "keyword1",
    "dba": "keyword1",
    "dbms_output": "keyword3",
    "debugoff": "keyword1",
    "debugon": "keyword1",
    "decimal": "keyword1",
    "declare": "keyword1",
    "decode": "keyword2",
    "default": "keyword1",
    "define": "keyword2",
    "definition": "keyword1",
    "delay": "keyword1",
    "delete": "keyword1",
    "desc": "keyword1",
    "digits": "keyword1",
    "dispose": "keyword1",
    "distinct": "keyword1",
    "do": "keyword1",
    "drop": "keyword1",
    "dump": "keyword1",
    "else": "keyword1",
    "elsif": "keyword1",
    "enable": "keyword3",
    "end": "keyword1",
    "entry": "keyword1",
    "exception": "keyword1",
    "exception_init": "keyword1",
    "exclusive": "keyword1",
    "exists": "keyword1",
    "exit": "keyword1",
    "external": "keyword1",
    "false": "keyword1",
    "fclose": "keyword3",
    "fclose_all": "keyword3",
    "fetch": "keyword1",
    "file": "keyword1",
    "file_type": "keyword3",
    "float": "keyword1",
    "floor": "keyword2",
    "fopen": "keyword3",
    "for": "keyword1",
    "form": "keyword1",
    "from": "keyword1",
    "function": "keyword1",
    "generic": "keyword1",
    "goto": "keyword1",
    "grant": "keyword1",
    "greatest": "keyword1",
    "group": "keyword1",
    "having": "keyword1",
    "hextoraw": "keyword2",
    "identified": "keyword1",
    "identitycol": "keyword1",
    "if": "keyword1",
    "image": "keyword1",
    "immediate": "keyword1",
    "in": "keyword1",
    "increment": "keyword1",
    "index": "keyword1",
    "indexes": "keyword1",
    "indicator": "keyword1",
    "initcap": "keyword2",
    "initial": "keyword1",
    "insert": "keyword1",
    "instr": "keyword2",
    "instrb": "keyword2",
    "int": "keyword1",
    "integer": "keyword1",
    "interface": "keyword1",
    "intersect": "keyword1",
    "into": "keyword1",
    "invalid_operation": "keyword3",
    "invalid_path": "keyword3",
    "is": "keyword1",
    "isopen": "keyword1",
    "key": "keyword1",
    "last_day": "keyword2",
    "least": "keyword1",
    "length": "keyword2",
    "lengthb": "keyword2",
    "level": "keyword1",
    "like": "keyword1",
    "limited": "keyword1",
    "linesize": "keyword3",
    "ln": "keyword2",
    "lock": "keyword1",
    "log": "keyword2",
    "long": "keyword1",
    "loop": "keyword1",
    "lower": "keyword2",
    "lpad": "keyword2",
    "ltrim": "keyword2",
    "matched": "keyword1",
    "max": "keyword1",
    "maxextents": "keyword1",
    "merge": "keyword1",
    "min": "keyword1",
    "minus": "keyword1",
    "mlslabel": "keyword1",
    "mod": "keyword2",
    "money": "keyword1",
    "months_between": "keyword2",
    "more": "keyword1",
    "name": "keyword1",
    "natural": "keyword1",
    "naturaln": "keyword1",
    "nchar": "keyword1",
    "new": "keyword1",
    "new_time": "keyword2",
    "next": "keyword1",
    "next_day": "keyword2",
    "nextval": "keyword1",
    "nls_lower": "keyword2",
    "nls_upper": "keyword2",
    "nlssort": "keyword2",
    "noaudit": "keyword1",
    "nocompress": "keyword1",
    "not": "keyword1",
    "notfound": "keyword1",
    "nowait": "keyword1",
    "nsl_initcap": "keyword2",
    "ntext": "keyword1",
    "null": "keyword1",
    "number": "keyword1",
    "number_base": "keyword1",
    "numeric": "keyword1",
    "nvarchar": "keyword1",
    "nvl": "keyword2",
    "of": "keyword1",
    "off": "keyword1",
    "offline": "keyword1",
    "on": "keyword1",
    "online": "keyword1",
    "open": "keyword1",
    "option": "keyword1",
    "or": "keyword1",
    "order": "keyword1",
    "organization": "keyword1",
    "others": "keyword1",
    "out": "keyword1",
    "package": "keyword1",
    "pagesize": "keyword3",
    "partition": "keyword1",
    "pctfree": "keyword1",
    "pctincrease": "keyword1",
    "pls_integer": "keyword1",
    "positive": "keyword1",
    "positiven": "keyword1",
    "power": "keyword2",
    "pragma": "keyword1",
    "primary": "keyword1",
    "private": "keyword1",
    "privileges": "keyword1",
    "procedure": "keyword1",
    "prompt": "keyword1",
    "public": "keyword1",
    "put_line": "keyword3",
    "putf": "keyword3",
    "quoted_identifier": "keyword1",
    "raise": "keyword1",
    "range": "keyword1",
    "raw": "keyword1",
    "rawtohex": "keyword2",
    "real": "keyword1",
    "record": "keyword1",
    "ref": "keyword1",
    "release": "keyword1",
    "remr": "keyword1",
    "rename": "keyword1",
    "replace": "keyword2",
    "resource": "keyword1",
    "return": "keyword1",
    "reverse": "keyword1",
    "revoke": "keyword1",
    "rollback": "keyword1",
    "round": "keyword2",
    "row": "keyword1",
    "rowid": "keyword1",
    "rowidtochar": "keyword2",
    "rowlabel": "keyword1",
    "rownum": "keyword1",
    "rows": "keyword1",
    "rowtype": "keyword1",
    "rpad": "keyword2",
    "rtrim": "keyword2",
    "run": "keyword1",
    "savepoint": "keyword1",
    "schema": "keyword1",
    "select": "keyword1",
    "seperate": "keyword1",
    "serveroutput": "keyword3",
    "session": "keyword1",
    "set": "keyword1",
    "share": "keyword1",
    "sign": "keyword2",
    "signtype": "keyword1",
    "sin": "keyword2",
    "sinh": "keyword2",
    "smalldatetime": "keyword1",
    "smallint": "keyword1",
    "smallmoney": "keyword1",
    "soundex": "keyword2",
    "space": "keyword1",
    "spool": "keyword1",
    "sql": "keyword1",
    "sqlcode": "keyword1",
    "sqlerrm": "keyword1",
    "sqrt": "keyword2",
    "start": "keyword1",
    "statement": "keyword1",
    "stddev": "keyword1",
    "storage": "keyword1",
    "substr": "keyword2",
    "substrb": "keyword2",
    "subtype": "keyword1",
    "successfull": "keyword1",
    "sum": "keyword1",
    "synonym": "keyword1",
    "sysdate": "keyword1",
    "tabauth": "keyword1",
    "table": "keyword1",
    "tables": "keyword1",
    "tablespace": "keyword1",
    "tan": "keyword2",
    "tanh": "keyword2",
    "task": "keyword1",
    "terminate": "keyword1",
    "text": "keyword1",
    "then": "keyword1",
    "timestamp": "keyword1",
    "tinyint": "keyword1",
    "to": "keyword1",
    "to_char": "keyword2",
    "to_date": "keyword2",
    "to_multibyte": "keyword2",
    "to_number": "keyword2",
    "to_single_byte": "keyword2",
    "translate": "keyword2",
    "trigger": "keyword1",
    "true": "keyword1",
    "trunc": "keyword2",
    "truncate": "keyword1",
    "type": "keyword1",
    "uid": "keyword1",
    "union": "keyword1",
    "unique": "keyword1",
    "uniqueidentifier": "keyword1",
    "update": "keyword1",
    "updatetext": "keyword1",
    "upper": "keyword2",
    "use": "keyword1",
    "user": "keyword1",
    "using": "keyword1",
    "utl_file": "keyword3",
    "validate": "keyword1",
    "values": "keyword1",
    "varbinary": "keyword1",
    "varchar": "keyword1",
    "varchar2": "keyword1",
    "variance": "keyword1",
    "verify": "keyword3",
    "view": "keyword1",
    "views": "keyword1",
    "when": "keyword1",
    "whenever": "keyword1",
    "where": "keyword1",
    "while": "keyword1",
    "with": "keyword1",
    "work": "keyword1",
    "write": "keyword1",
    "write_error": "keyword3",
    "xor": "keyword1",
}

# Dictionary of keywords dictionaries for plsql mode.
keywordsDictDict = {
    "plsql_main": plsql_main_keywords_dict,
}

# Rules for plsql_main ruleset.

def plsql_rule0(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="/*", end="*/")

def plsql_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def plsql_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def plsql_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="[", end="]",
          no_line_break=True)

def plsql_rule4(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def plsql_rule5(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="REM",
          at_line_start=True)

def plsql_rule6(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="REMARK",
          at_line_start=True)

def plsql_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def plsql_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def plsql_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def plsql_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def plsql_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def plsql_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def plsql_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def plsql_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def plsql_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def plsql_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def plsql_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def plsql_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def plsql_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!=")

def plsql_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!>")

def plsql_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!<")

def plsql_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def plsql_rule23(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=":",
          at_line_start=True)

def plsql_rule24(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for plsql_main ruleset.
rulesDict1 = {
    "!": [plsql_rule19, plsql_rule20, plsql_rule21,],
    "\"": [plsql_rule2,],
    "%": [plsql_rule14,],
    "&": [plsql_rule15,],
    "'": [plsql_rule1,],
    "*": [plsql_rule10,],
    "+": [plsql_rule7,],
    "-": [plsql_rule4, plsql_rule8,],
    "/": [plsql_rule0, plsql_rule9,],
    "0": [plsql_rule24,],
    "1": [plsql_rule24,],
    "2": [plsql_rule24,],
    "3": [plsql_rule24,],
    "4": [plsql_rule24,],
    "5": [plsql_rule24,],
    "6": [plsql_rule24,],
    "7": [plsql_rule24,],
    "8": [plsql_rule24,],
    "9": [plsql_rule24,],
    ":": [plsql_rule22, plsql_rule23,],
    "<": [plsql_rule13,],
    "=": [plsql_rule11,],
    ">": [plsql_rule12,],
    "@": [plsql_rule24,],
    "A": [plsql_rule24,],
    "B": [plsql_rule24,],
    "C": [plsql_rule24,],
    "D": [plsql_rule24,],
    "E": [plsql_rule24,],
    "F": [plsql_rule24,],
    "G": [plsql_rule24,],
    "H": [plsql_rule24,],
    "I": [plsql_rule24,],
    "J": [plsql_rule24,],
    "K": [plsql_rule24,],
    "L": [plsql_rule24,],
    "M": [plsql_rule24,],
    "N": [plsql_rule24,],
    "O": [plsql_rule24,],
    "P": [plsql_rule24,],
    "Q": [plsql_rule24,],
    "R": [plsql_rule5, plsql_rule6, plsql_rule24,],
    "S": [plsql_rule24,],
    "T": [plsql_rule24,],
    "U": [plsql_rule24,],
    "V": [plsql_rule24,],
    "W": [plsql_rule24,],
    "X": [plsql_rule24,],
    "Y": [plsql_rule24,],
    "Z": [plsql_rule24,],
    "[": [plsql_rule3,],
    "^": [plsql_rule17,],
    "_": [plsql_rule24,],
    "a": [plsql_rule24,],
    "b": [plsql_rule24,],
    "c": [plsql_rule24,],
    "d": [plsql_rule24,],
    "e": [plsql_rule24,],
    "f": [plsql_rule24,],
    "g": [plsql_rule24,],
    "h": [plsql_rule24,],
    "i": [plsql_rule24,],
    "j": [plsql_rule24,],
    "k": [plsql_rule24,],
    "l": [plsql_rule24,],
    "m": [plsql_rule24,],
    "n": [plsql_rule24,],
    "o": [plsql_rule24,],
    "p": [plsql_rule24,],
    "q": [plsql_rule24,],
    "r": [plsql_rule24,],
    "s": [plsql_rule24,],
    "t": [plsql_rule24,],
    "u": [plsql_rule24,],
    "v": [plsql_rule24,],
    "w": [plsql_rule24,],
    "x": [plsql_rule24,],
    "y": [plsql_rule24,],
    "z": [plsql_rule24,],
    "|": [plsql_rule16,],
    "~": [plsql_rule18,],
}

# x.rulesDictDict for plsql mode.
rulesDictDict = {
    "plsql_main": rulesDict1,
}

# Import dict for plsql mode.
importDict = {}
