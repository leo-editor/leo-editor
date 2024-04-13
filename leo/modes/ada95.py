# Leo colorizer control file for ada95 mode.
# This file is in the public domain.

# Properties for ada95 mode.
properties = {
    "lineComment": "--",
}

# Attributes dict for ada95_main ruleset.
ada95_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "",
    "highlight_digits": "true",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for ada95 mode.
attributesDictDict = {
    "ada95_main": ada95_main_attributes_dict,
}

# Keywords dict for ada95_main ruleset.
ada95_main_keywords_dict = {
    "abort": "keyword2",
    "abs": "keyword2",
    "abstract": "keyword2",
    "accept": "keyword2",
    "access": "keyword2",
    "address": "literal2",
    "aliased": "keyword2",
    "all": "keyword2",
    "and": "keyword2",
    "array": "keyword2",
    "at": "keyword2",
    "begin": "keyword2",
    "body": "keyword2",
    "boolean": "literal2",
    "case": "keyword2",
    "character": "literal2",
    "constant": "keyword2",
    "declare": "keyword2",
    "delay": "keyword2",
    "delta": "keyword2",
    "digits": "keyword2",
    "do": "keyword2",
    "duration": "literal2",
    "else": "keyword2",
    "elsif": "keyword2",
    "end": "keyword2",
    "entry": "keyword1",
    "exception": "keyword2",
    "exit": "keyword2",
    "false": "literal1",
    "float": "literal2",
    "for": "keyword2",
    "function": "keyword1",
    "goto": "keyword2",
    "if": "keyword2",
    "in": "keyword2",
    "integer": "literal2",
    "is": "keyword2",
    "latin_1": "literal2",
    "limited": "keyword2",
    "loop": "keyword2",
    "mod": "keyword2",
    "natural": "literal2",
    "new": "keyword2",
    "not": "keyword2",
    "null": "literal1",
    "or": "keyword2",
    "others": "keyword2",
    "out": "keyword2",
    "package": "keyword2",
    "positive": "literal2",
    "pragma": "keyword2",
    "private": "keyword2",
    "procedure": "keyword1",
    "protected": "keyword2",
    "raise": "keyword2",
    "range": "keyword2",
    "record": "keyword2",
    "rem": "keyword2",
    "renames": "keyword2",
    "requeue": "keyword2",
    "return": "keyword2",
    "select": "keyword2",
    "separate": "keyword2",
    "string": "literal2",
    "subtype": "keyword2",
    "tagged": "keyword2",
    "task": "keyword2",
    "terminate": "keyword2",
    "then": "keyword2",
    "time": "literal2",
    "true": "literal1",
    "type": "keyword2",
    "until": "keyword2",
    "use": "keyword2",
    "when": "keyword2",
    "while": "keyword2",
    "with": "keyword2",
    "xor": "keyword2",
}

# Dictionary of keywords dictionaries for ada95 mode.
keywordsDictDict = {
    "ada95_main": ada95_main_keywords_dict,
}

# Rules for ada95_main ruleset.

def ada95_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="--")

def ada95_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def ada95_rule2(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=")")

def ada95_rule3(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="(")

def ada95_rule4(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="..")

def ada95_rule5(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=".all")

def ada95_rule6(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=":=")

def ada95_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/=")

def ada95_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=>")

def ada95_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def ada95_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="null", seq="<>")

def ada95_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="label", seq="<<")

def ada95_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="label", seq=">>")

def ada95_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def ada95_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def ada95_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def ada95_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def ada95_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def ada95_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def ada95_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def ada95_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def ada95_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="**")

def ada95_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def ada95_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'access")

def ada95_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'address")

def ada95_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'adjacent")

def ada95_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'aft")

def ada95_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'alignment")

def ada95_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'base")

def ada95_rule29(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'bit_order")

def ada95_rule30(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'body_version")

def ada95_rule31(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'callable")

def ada95_rule32(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'caller")

def ada95_rule33(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'ceiling")

def ada95_rule34(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'class")

def ada95_rule35(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'component_size")

def ada95_rule36(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'composed")

def ada95_rule37(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'constrained")

def ada95_rule38(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'copy_size")

def ada95_rule39(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'count")

def ada95_rule40(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'definite")

def ada95_rule41(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'delta")

def ada95_rule42(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'denorm")

def ada95_rule43(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'digits")

def ada95_rule44(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'exponent")

def ada95_rule45(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'external_tag")

def ada95_rule46(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'first")

def ada95_rule47(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'first_bit")

def ada95_rule48(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'floor")

def ada95_rule49(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'fore")

def ada95_rule50(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'fraction")

def ada95_rule51(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'genetic")

def ada95_rule52(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'identity")

def ada95_rule53(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'image")

def ada95_rule54(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'input")

def ada95_rule55(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'last")

def ada95_rule56(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'last_bit")

def ada95_rule57(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'leading_part")

def ada95_rule58(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'length")

def ada95_rule59(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'machine")

def ada95_rule60(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'machine_emax")

def ada95_rule61(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'machine_emin")

def ada95_rule62(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'machine_mantissa")

def ada95_rule63(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'machine_overflows")

def ada95_rule64(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'machine_radix")

def ada95_rule65(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'machine_rounds")

def ada95_rule66(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'max")

def ada95_rule67(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'max_size_in_storage_elements")

def ada95_rule68(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'min")

def ada95_rule69(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'model")

def ada95_rule70(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'model_emin")

def ada95_rule71(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'model_epsilon")

def ada95_rule72(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'model_mantissa")

def ada95_rule73(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'model_small")

def ada95_rule74(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'modulus")

def ada95_rule75(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'output")

def ada95_rule76(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'partition_id")

def ada95_rule77(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'pos")

def ada95_rule78(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'position")

def ada95_rule79(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'pred")

def ada95_rule80(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'range")

def ada95_rule81(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'read")

def ada95_rule82(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'remainder")

def ada95_rule83(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'round")

def ada95_rule84(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'rounding")

def ada95_rule85(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'safe_first")

def ada95_rule86(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'safe_last")

def ada95_rule87(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'scale")

def ada95_rule88(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'scaling")

def ada95_rule89(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'signed_zeros")

def ada95_rule90(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'size")

def ada95_rule91(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'small")

def ada95_rule92(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'storage_pool")

def ada95_rule93(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'storage_size")

def ada95_rule94(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'succ")

def ada95_rule95(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'tag")

def ada95_rule96(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'terminated")

def ada95_rule97(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'truncation")

def ada95_rule98(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'unbiased_rounding")

def ada95_rule99(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'unchecked_access")

def ada95_rule100(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'val")

def ada95_rule101(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'valid")

def ada95_rule102(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'value")

def ada95_rule103(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'version")

def ada95_rule104(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'wide_image")

def ada95_rule105(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'wide_value")

def ada95_rule106(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'wide_width")

def ada95_rule107(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'width")

def ada95_rule108(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="keyword3", seq="'write")

def ada95_rule109(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def ada95_rule110(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for ada95_main ruleset.
rulesDict1 = {
    "\"": [ada95_rule1,],
    "&": [ada95_rule17,],
    "'": [ada95_rule23, ada95_rule24, ada95_rule25, ada95_rule26, ada95_rule27, ada95_rule28, ada95_rule29, ada95_rule30, ada95_rule31, ada95_rule32, ada95_rule33, ada95_rule34, ada95_rule35, ada95_rule36, ada95_rule37, ada95_rule38, ada95_rule39, ada95_rule40, ada95_rule41, ada95_rule42, ada95_rule43, ada95_rule44, ada95_rule45, ada95_rule46, ada95_rule47, ada95_rule48, ada95_rule49, ada95_rule50, ada95_rule51, ada95_rule52, ada95_rule53, ada95_rule54, ada95_rule55, ada95_rule56, ada95_rule57, ada95_rule58, ada95_rule59, ada95_rule60, ada95_rule61, ada95_rule62, ada95_rule63, ada95_rule64, ada95_rule65, ada95_rule66, ada95_rule67, ada95_rule68, ada95_rule69, ada95_rule70, ada95_rule71, ada95_rule72, ada95_rule73, ada95_rule74, ada95_rule75, ada95_rule76, ada95_rule77, ada95_rule78, ada95_rule79, ada95_rule80, ada95_rule81, ada95_rule82, ada95_rule83, ada95_rule84, ada95_rule85, ada95_rule86, ada95_rule87, ada95_rule88, ada95_rule89, ada95_rule90, ada95_rule91, ada95_rule92, ada95_rule93, ada95_rule94, ada95_rule95, ada95_rule96, ada95_rule97, ada95_rule98, ada95_rule99, ada95_rule100, ada95_rule101, ada95_rule102, ada95_rule103, ada95_rule104, ada95_rule105, ada95_rule106, ada95_rule107, ada95_rule108, ada95_rule109,],
    "(": [ada95_rule3,],
    ")": [ada95_rule2,],
    "*": [ada95_rule21, ada95_rule22,],
    "+": [ada95_rule18,],
    "-": [ada95_rule0, ada95_rule19,],
    ".": [ada95_rule4, ada95_rule5,],
    "/": [ada95_rule7, ada95_rule20,],
    "0": [ada95_rule110,],
    "1": [ada95_rule110,],
    "2": [ada95_rule110,],
    "3": [ada95_rule110,],
    "4": [ada95_rule110,],
    "5": [ada95_rule110,],
    "6": [ada95_rule110,],
    "7": [ada95_rule110,],
    "8": [ada95_rule110,],
    "9": [ada95_rule110,],
    ":": [ada95_rule6,],
    "<": [ada95_rule10, ada95_rule11, ada95_rule14, ada95_rule16,],
    "=": [ada95_rule8, ada95_rule9,],
    ">": [ada95_rule12, ada95_rule13, ada95_rule15,],
    "@": [ada95_rule110,],
    "A": [ada95_rule110,],
    "B": [ada95_rule110,],
    "C": [ada95_rule110,],
    "D": [ada95_rule110,],
    "E": [ada95_rule110,],
    "F": [ada95_rule110,],
    "G": [ada95_rule110,],
    "H": [ada95_rule110,],
    "I": [ada95_rule110,],
    "J": [ada95_rule110,],
    "K": [ada95_rule110,],
    "L": [ada95_rule110,],
    "M": [ada95_rule110,],
    "N": [ada95_rule110,],
    "O": [ada95_rule110,],
    "P": [ada95_rule110,],
    "Q": [ada95_rule110,],
    "R": [ada95_rule110,],
    "S": [ada95_rule110,],
    "T": [ada95_rule110,],
    "U": [ada95_rule110,],
    "V": [ada95_rule110,],
    "W": [ada95_rule110,],
    "X": [ada95_rule110,],
    "Y": [ada95_rule110,],
    "Z": [ada95_rule110,],
    "_": [ada95_rule110,],
    "a": [ada95_rule110,],
    "b": [ada95_rule110,],
    "c": [ada95_rule110,],
    "d": [ada95_rule110,],
    "e": [ada95_rule110,],
    "f": [ada95_rule110,],
    "g": [ada95_rule110,],
    "h": [ada95_rule110,],
    "i": [ada95_rule110,],
    "j": [ada95_rule110,],
    "k": [ada95_rule110,],
    "l": [ada95_rule110,],
    "m": [ada95_rule110,],
    "n": [ada95_rule110,],
    "o": [ada95_rule110,],
    "p": [ada95_rule110,],
    "q": [ada95_rule110,],
    "r": [ada95_rule110,],
    "s": [ada95_rule110,],
    "t": [ada95_rule110,],
    "u": [ada95_rule110,],
    "v": [ada95_rule110,],
    "w": [ada95_rule110,],
    "x": [ada95_rule110,],
    "y": [ada95_rule110,],
    "z": [ada95_rule110,],
}

# x.rulesDictDict for ada95 mode.
rulesDictDict = {
    "ada95_main": rulesDict1,
}

# Import dict for ada95 mode.
importDict = {}
