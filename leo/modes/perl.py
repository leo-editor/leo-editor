# Leo colorizer control file for perl mode.
# This file is in the public domain.

# Properties for perl mode.
properties = {
    "indentCloseBrackets": "}",
    "indentOpenBrackets": "{",
    "lineComment": "#",
    "lineUpClosingBracket": "true",
}

# Attributes dict for perl_main ruleset.
perl_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for perl_pod ruleset.
perl_pod_attributes_dict = {
    "default": "COMMENT2",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for perl_literal ruleset.
perl_literal_attributes_dict = {
    "default": "LITERAL1",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for perl_exec ruleset.
perl_exec_attributes_dict = {
    "default": "KEYWORD3",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for perl_variable ruleset.
perl_variable_attributes_dict = {
    "default": "KEYWORD2",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Attributes dict for perl_regexp ruleset.
perl_regexp_attributes_dict = {
    "default": "MARKUP",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "true",
    "ignore_case": "false",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for perl mode.
attributesDictDict = {
    "perl_exec": perl_exec_attributes_dict,
    "perl_literal": perl_literal_attributes_dict,
    "perl_main": perl_main_attributes_dict,
    "perl_pod": perl_pod_attributes_dict,
    "perl_regexp": perl_regexp_attributes_dict,
    "perl_variable": perl_variable_attributes_dict,
}

# Keywords dict for perl_main ruleset.
perl_main_keywords_dict = {
    "BEGIN": "keyword1",
    "END": "keyword1",
    "abs": "keyword3",
    "accept": "keyword3",
    "alarm": "keyword3",
    "and": "operator",
    "atan2": "keyword3",
    "bind": "keyword3",
    "binmode": "keyword3",
    "bless": "keyword3",
    "caller": "keyword1",
    "chdir": "keyword3",
    "chmod": "keyword3",
    "chomp": "keyword3",
    "chop": "keyword3",
    "chown": "keyword3",
    "chr": "keyword3",
    "chroot": "keyword3",
    "close": "keyword3",
    "closedir": "keyword3",
    "cmp": "operator",
    "connect": "keyword3",
    "continue": "keyword1",
    "cos": "keyword3",
    "crypt": "keyword3",
    "dbmclose": "keyword3",
    "dbmopen": "keyword3",
    "defined": "keyword3",
    "delete": "keyword3",
    "die": "keyword1",
    "do": "keyword1",
    "dump": "keyword1",
    "each": "keyword3",
    "else": "keyword1",
    "elsif": "keyword1",
    "endgrent": "keyword3",
    "endhostent": "keyword3",
    "endnetent": "keyword3",
    "endprotoent": "keyword3",
    "endpwent": "keyword3",
    "endservent": "keyword3",
    "eof": "keyword3",
    "eq": "operator",
    "eval": "keyword1",
    "exec": "keyword3",
    "exists": "keyword3",
    "exit": "keyword1",
    "exp": "keyword3",
    "fcntl": "keyword3",
    "fileno": "keyword3",
    "flock": "keyword3",
    "for": "keyword1",
    "foreach": "keyword1",
    "fork": "keyword3",
    "format": "keyword3",
    "formline": "keyword3",
    "ge": "operator",
    "getc": "keyword3",
    "getgrent": "keyword3",
    "getgrgid": "keyword3",
    "getgrnam": "keyword3",
    "gethostbyaddr": "keyword3",
    "gethostbyname": "keyword3",
    "gethostent": "keyword3",
    "getlogin": "keyword3",
    "getnetbyaddr": "keyword3",
    "getnetbyname": "keyword3",
    "getnetent": "keyword3",
    "getpeername": "keyword3",
    "getpgrp": "keyword3",
    "getppid": "keyword3",
    "getpriority": "keyword3",
    "getprotobyname": "keyword3",
    "getprotobynumber": "keyword3",
    "getprotoent": "keyword3",
    "getpwent": "keyword3",
    "getpwnam": "keyword3",
    "getpwuid": "keyword3",
    "getservbyname": "keyword3",
    "getservbyport": "keyword3",
    "getservent": "keyword3",
    "getsockname": "keyword3",
    "getsockopt": "keyword3",
    "glob": "keyword3",
    "gmtime": "keyword3",
    "goto": "keyword1",
    "grep": "keyword3",
    "hex": "keyword3",
    "if": "keyword1",
    "import": "keyword1",
    "index": "keyword3",
    "int": "keyword3",
    "ioctl": "keyword3",
    "join": "keyword3",
    "keys": "keyword3",
    "kill": "keyword3",
    "last": "keyword1",
    "lc": "keyword3",
    "lcfirst": "keyword3",
    "le": "operator",
    "length": "keyword3",
    "link": "keyword3",
    "listen": "keyword3",
    "local": "keyword1",
    "localtime": "keyword3",
    "log": "keyword3",
    "lstat": "keyword3",
    "map": "keyword3",
    "mkdir": "keyword3",
    "msgctl": "keyword3",
    "msgget": "keyword3",
    "msgrcv": "keyword3",
    "msgsnd": "keyword3",
    "my": "keyword1",
    "ne": "operator",
    "new": "keyword1",
    "next": "keyword1",
    "no": "keyword1",
    "not": "operator",
    "oct": "keyword3",
    "open": "keyword3",
    "opendir": "keyword3",
    "or": "operator",
    "ord": "keyword3",
    "our": "keyword1",
    "pack": "keyword3",
    "package": "keyword1",
    "pipe": "keyword3",
    "pop": "keyword3",
    "pos": "keyword3",
    "print": "keyword3",
    "printf": "keyword3",
    "push": "keyword3",
    "quotemeta": "keyword3",
    "rand": "keyword3",
    "read": "keyword3",
    "readdir": "keyword3",
    "readlink": "keyword3",
    "recv": "keyword3",
    "redo": "keyword1",
    "ref": "keyword3",
    "rename": "keyword3",
    "require": "keyword1",
    "reset": "keyword3",
    "return": "keyword1",
    "reverse": "keyword3",
    "rewinddir": "keyword3",
    "rindex": "keyword3",
    "rmdir": "keyword3",
    "scalar": "keyword3",
    "seek": "keyword3",
    "seekdir": "keyword3",
    "select": "keyword3",
    "semctl": "keyword3",
    "semget": "keyword3",
    "semop": "keyword3",
    "send": "keyword3",
    "setgrent": "keyword3",
    "sethostent": "keyword3",
    "setnetent": "keyword3",
    "setpgrp": "keyword3",
    "setpriority": "keyword3",
    "setprotoent": "keyword3",
    "setpwent": "keyword3",
    "setservent": "keyword3",
    "setsockopt": "keyword3",
    "shift": "keyword3",
    "shmctl": "keyword3",
    "shmget": "keyword3",
    "shmread": "keyword3",
    "shmwrite": "keyword3",
    "shutdown": "keyword3",
    "sin": "keyword3",
    "sleep": "keyword3",
    "socket": "keyword3",
    "socketpair": "keyword3",
    "sort": "keyword3",
    "splice": "keyword3",
    "split": "keyword3",
    "sprintf": "keyword3",
    "sqrt": "keyword3",
    "srand": "keyword3",
    "stat": "keyword3",
    "study": "keyword3",
    "sub": "keyword1",
    "substr": "keyword3",
    "symlink": "keyword3",
    "syscall": "keyword3",
    "sysread": "keyword3",
    "sysseek": "keyword3",
    "system": "keyword3",
    "syswrite": "keyword3",
    "tell": "keyword3",
    "telldir": "keyword3",
    "tie": "keyword3",
    "tied": "keyword3",
    "time": "keyword3",
    "times": "keyword3",
    "truncate": "keyword3",
    "uc": "keyword3",
    "ucfirst": "keyword3",
    "umask": "keyword3",
    "undef": "keyword3",
    "unless": "keyword1",
    "unlink": "keyword3",
    "unpack": "keyword3",
    "unshift": "keyword3",
    "untie": "keyword3",
    "until": "keyword1",
    "use": "keyword1",
    "utime": "keyword3",
    "values": "keyword3",
    "vec": "keyword3",
    "wait": "keyword3",
    "waitpid": "keyword3",
    "wantarray": "keyword1",
    "warn": "keyword3",
    "while": "keyword1",
    "write": "keyword3",
    "x": "operator",
    "xor": "operator",
}

# Keywords dict for perl_pod ruleset.
perl_pod_keywords_dict = {}

# Keywords dict for perl_literal ruleset.
perl_literal_keywords_dict = {}

# Keywords dict for perl_exec ruleset.
perl_exec_keywords_dict = {}

# Keywords dict for perl_variable ruleset.
perl_variable_keywords_dict = {}

# Keywords dict for perl_regexp ruleset.
perl_regexp_keywords_dict = {}

# Dictionary of keywords dictionaries for perl mode.
keywordsDictDict = {
    "perl_exec": perl_exec_keywords_dict,
    "perl_literal": perl_literal_keywords_dict,
    "perl_main": perl_main_keywords_dict,
    "perl_pod": perl_pod_keywords_dict,
    "perl_regexp": perl_regexp_keywords_dict,
    "perl_variable": perl_variable_keywords_dict,
}

# Rules for perl_main ruleset.

def perl_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def perl_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=head1", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=head2", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=head3", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=head4", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=item", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule6(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=over", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule7(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=back", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=pod", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule9(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=for", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule10(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=begin", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule11(colorer, s, i):
    return colorer.match_span(s, i, kind="label", begin="=end", end="=cut",
          at_line_start=True,
          delegate="perl::pod")

def perl_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="$`")

def perl_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="$'")

def perl_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword2", seq="$\"")

def perl_rule15(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          delegate="perl::variable",
          no_line_break=True)

def perl_rule16(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="\\$(?:#|\\w)+")

def perl_rule17(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="@(?:#|\\w)+")

def perl_rule18(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="keyword2", regexp="%(?:#|\\w)+")

def perl_rule19(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="@{", end="}",
          delegate="perl::variable",
          no_line_break=True)

def perl_rule20(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="%{", end="}",
          delegate="perl::variable",
          no_line_break=True)

def perl_rule21(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"")

def perl_rule22(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'")

def perl_rule23(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword3", begin="`", end="`",
          delegate="perl::exec")

def perl_rule24(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal2", begin="<<[:space:]*(['\"])([[:space:][:alnum:]_]*)\\1;?\\s*", end="$2",
          delegate="perl::literal")

def perl_rule25(colorer, s, i):
    return colorer.match_span_regexp(s, i, kind="literal2", begin="<<([[:alpha:]_][[:alnum:]_]*);?\\s*", end="$1",
          delegate="perl::literal")

def perl_rule26(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="/[^[:blank:]]*?[^\\\\]/")

def perl_rule27(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="q(?:|[qrx])\\{(?:.*?[^\\\\])*?\\}")

def perl_rule28(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="tr([[:punct:]])(?:.*?[^\\\\])*?\\1(?:.*?[^\\\\])*?\\1")

def perl_rule29(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="y([[:punct:]])(?:.*?[^\\\\])*?\\1(?:.*?[^\\\\])*?\\1")

def perl_rule30(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="m\\{(?:.*?[^\\\\])*?\\}[sgiexom]*")

def perl_rule31(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="m([[:punct:]])(?:.*?[^\\\\])*?\\1[sgiexom]*")

def perl_rule32(colorer, s, i):
    return 0  # too complicated
    # return colorer.match_seq_regexp(s, i, kind="markup", regexp="s\\s*\\{(?:.*?[^\\\\])*?\\}\\s*\\{(?:.*?[^\\\\])*?\\}[sgiexom]*",
    #       )

def perl_rule33(colorer, s, i):
    return 0  # too complicated
    # return colorer.match_seq_regexp(s, i, kind="markup", regexp="s([[:punct:]])(?:.*?[^\\\\])*?\\1(?:.*?[^\\\\])*?\\1[sgiexom]*",
    #       )

def perl_rule34(colorer, s, i):
    return colorer.match_seq_regexp(s, i, kind="markup", regexp="/[^[:blank:]]*?/")

def perl_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def perl_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def perl_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def perl_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def perl_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def perl_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def perl_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def perl_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def perl_rule43(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def perl_rule44(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def perl_rule45(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def perl_rule46(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def perl_rule47(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def perl_rule48(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def perl_rule49(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def perl_rule50(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="}")

def perl_rule51(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="{")

def perl_rule52(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="?")

def perl_rule53(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":")

def perl_rule54(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for perl_main ruleset.
rulesDict1 = {
    "!": [perl_rule37, perl_rule43,],
    "\"": [perl_rule21,],
    "#": [perl_rule0,],
    "$": [perl_rule12, perl_rule13, perl_rule14, perl_rule15, perl_rule16,],
    "%": [perl_rule18, perl_rule20,],
    "&": [perl_rule36,],
    "'": [perl_rule22,],
    "*": [perl_rule47,],
    "+": [perl_rule44,],
    "-": [perl_rule45,],
    "/": [perl_rule26, perl_rule34, perl_rule46,],
    "0": [perl_rule54,],
    "1": [perl_rule54,],
    "2": [perl_rule54,],
    "3": [perl_rule54,],
    "4": [perl_rule54,],
    "5": [perl_rule54,],
    "6": [perl_rule54,],
    "7": [perl_rule54,],
    "8": [perl_rule54,],
    "9": [perl_rule54,],
    ":": [perl_rule53,],
    "<": [perl_rule24, perl_rule25, perl_rule39, perl_rule41,],
    "=": [perl_rule1, perl_rule2, perl_rule3, perl_rule4, perl_rule5, perl_rule6, perl_rule7, perl_rule8, perl_rule9, perl_rule10, perl_rule11, perl_rule42,],
    ">": [perl_rule38, perl_rule40,],
    "?": [perl_rule52,],
    "@": [perl_rule17, perl_rule19, perl_rule54,],
    "A": [perl_rule54,],
    "B": [perl_rule54,],
    "C": [perl_rule54,],
    "D": [perl_rule54,],
    "E": [perl_rule54,],
    "F": [perl_rule54,],
    "G": [perl_rule54,],
    "H": [perl_rule54,],
    "I": [perl_rule54,],
    "J": [perl_rule54,],
    "K": [perl_rule54,],
    "L": [perl_rule54,],
    "M": [perl_rule54,],
    "N": [perl_rule54,],
    "O": [perl_rule54,],
    "P": [perl_rule54,],
    "Q": [perl_rule54,],
    "R": [perl_rule54,],
    "S": [perl_rule54,],
    "T": [perl_rule54,],
    "U": [perl_rule54,],
    "V": [perl_rule54,],
    "W": [perl_rule54,],
    "X": [perl_rule54,],
    "Y": [perl_rule54,],
    "Z": [perl_rule54,],
    "^": [perl_rule48,],
    "`": [perl_rule23,],
    "a": [perl_rule54,],
    "b": [perl_rule54,],
    "c": [perl_rule54,],
    "d": [perl_rule54,],
    "e": [perl_rule54,],
    "f": [perl_rule54,],
    "g": [perl_rule54,],
    "h": [perl_rule54,],
    "i": [perl_rule54,],
    "j": [perl_rule54,],
    "k": [perl_rule54,],
    "l": [perl_rule54,],
    "m": [perl_rule30, perl_rule31, perl_rule54,],
    "n": [perl_rule54,],
    "o": [perl_rule54,],
    "p": [perl_rule54,],
    "q": [perl_rule27, perl_rule54,],
    "r": [perl_rule54,],
    "s": [perl_rule32, perl_rule33, perl_rule54,],
    "t": [perl_rule28, perl_rule54,],
    "u": [perl_rule54,],
    "v": [perl_rule54,],
    "w": [perl_rule54,],
    "x": [perl_rule54,],
    "y": [perl_rule29, perl_rule54,],
    "z": [perl_rule54,],
    "{": [perl_rule51,],
    "|": [perl_rule35,],
    "}": [perl_rule50,],
    "~": [perl_rule49,],
}

# Rules for perl_pod ruleset.

# Rules dict for perl_pod ruleset.
rulesDict2 = {}

# Rules for perl_literal ruleset.

def perl_rule55(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          delegate="perl::variable",
          no_line_break=True)

def perl_rule56(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="@{", end="}",
          delegate="perl::variable",
          no_line_break=True)

def perl_rule57(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="%{", end="}",
          delegate="perl::variable",
          no_line_break=True)

def perl_rule58(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="|")

def perl_rule59(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="&")

def perl_rule60(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="!")

def perl_rule61(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq=">")

def perl_rule62(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="<")

def perl_rule63(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq=")")

def perl_rule64(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="(")

def perl_rule65(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="=")

def perl_rule66(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="!")

def perl_rule67(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="+")

def perl_rule68(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="-")

def perl_rule69(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="/")

def perl_rule70(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="*")

def perl_rule71(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="^")

def perl_rule72(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="~")

def perl_rule73(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="}")

def perl_rule74(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="{")

def perl_rule75(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq=".")

def perl_rule76(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq=",")

def perl_rule77(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq=";")

def perl_rule78(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="]")

def perl_rule79(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="[")

def perl_rule80(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq="?")

def perl_rule81(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="literal1", seq=":")

# Rules dict for perl_literal ruleset.
rulesDict3 = {
    "!": [perl_rule60, perl_rule66,],
    "$": [perl_rule55,],
    "%": [perl_rule57,],
    "&": [perl_rule59,],
    "(": [perl_rule64,],
    ")": [perl_rule63,],
    "*": [perl_rule70,],
    "+": [perl_rule67,],
    ",": [perl_rule76,],
    "-": [perl_rule68,],
    ".": [perl_rule75,],
    "/": [perl_rule69,],
    ":": [perl_rule81,],
    ";": [perl_rule77,],
    "<": [perl_rule62,],
    "=": [perl_rule65,],
    ">": [perl_rule61,],
    "?": [perl_rule80,],
    "@": [perl_rule56,],
    "[": [perl_rule79,],
    "]": [perl_rule78,],
    "^": [perl_rule71,],
    "{": [perl_rule74,],
    "|": [perl_rule58,],
    "}": [perl_rule73,],
    "~": [perl_rule72,],
}

# Rules for perl_exec ruleset.

def perl_rule82(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#")

def perl_rule83(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="${", end="}",
          no_line_break=True)

def perl_rule84(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="@{", end="}",
          no_line_break=True)

def perl_rule85(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="%{", end="}",
          no_line_break=True)

# Rules dict for perl_exec ruleset.
rulesDict4 = {
    "#": [perl_rule82,],
    "$": [perl_rule83,],
    "%": [perl_rule85,],
    "@": [perl_rule84,],
}

# Rules for perl_variable ruleset.

def perl_rule86(colorer, s, i):
    return colorer.match_span(s, i, kind="keyword2", begin="{", end="}",
          delegate="perl::variable",
          no_line_break=True)

def perl_rule87(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="->")

# Rules dict for perl_variable ruleset.
rulesDict5 = {
    "-": [perl_rule87,],
    "{": [perl_rule86,],
}

# Rules for perl_regexp ruleset.

def perl_rule88(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq=")(")

def perl_rule89(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq=")[")

def perl_rule90(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="){")

def perl_rule91(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="](")

def perl_rule92(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="][")

def perl_rule93(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="]{")

def perl_rule94(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="}(")

def perl_rule95(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="}[")

def perl_rule96(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="markup", seq="}{")

def perl_rule97(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="(", end=")",
          delegate="perl::regexp")

def perl_rule98(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="[", end="]",
          delegate="perl::regexp")

def perl_rule99(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="{", end="}",
          delegate="perl::regexp")

# Rules dict for perl_regexp ruleset.
rulesDict6 = {
    "(": [perl_rule97,],
    ")": [perl_rule88, perl_rule89, perl_rule90,],
    "[": [perl_rule98,],
    "]": [perl_rule91, perl_rule92, perl_rule93,],
    "{": [perl_rule99,],
    "}": [perl_rule94, perl_rule95, perl_rule96,],
}

# x.rulesDictDict for perl mode.
rulesDictDict = {
    "perl_exec": rulesDict4,
    "perl_literal": rulesDict3,
    "perl_main": rulesDict1,
    "perl_pod": rulesDict2,
    "perl_regexp": rulesDict6,
    "perl_variable": rulesDict5,
}

# Import dict for perl mode.
importDict = {}
