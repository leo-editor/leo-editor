# Leo colorizer control file for assembly_6502 mode.
# This file is in the public domain.

# Properties for assembly_6502 mode.
properties = {
        "lineComment": ";",
}

# Attributes dict for assembly_6502_main ruleset.
assembly_6502_main_attributes_dict = {
        "default": "null",
        "digit_re": "",
        "escape": "",
        "highlight_digits": "true",
        "ignore_case": "true",
        "no_word_sep": "",
}

# Dictionary of attributes dictionaries for assembly_6502 mode.
attributesDictDict = {
        "assembly_6502_main": assembly_6502_main_attributes_dict,
}

# Keywords dict for assembly_6502_main ruleset.
assembly_6502_main_keywords_dict = {
        "a": "keyword3",
        "adc": "function",
        "add": "function",
        "and": "function",
        "asl": "function",
        "bcc": "function",
        "bcs": "function",
        "beq": "function",
        "bit": "function",
        "bmi": "function",
        "bne": "function",
        "bpl": "function",
        "brk": "function",
        "bvc": "function",
        "bvs": "function",
        "clc": "function",
        "cld": "function",
        "cli": "function",
        "clv": "function",
        "cmp": "function",
        "cpx": "function",
        "cpy": "function",
        "dec": "function",
        "defseg": "keyword1",
        "dex": "function",
        "dey": "function",
        "dta": "keyword1",
        "eif": "keyword1",
        "eli": "keyword1",
        "els": "keyword1",
        "end": "keyword1",
        "eor": "function",
        "equ": "keyword1",
        "ert": "keyword1",
        "icl": "keyword1",
        "ift": "keyword1",
        "inc": "function",
        "ini": "keyword1",
        "ins": "keyword1",
        "inw": "function",
        "inx": "function",
        "iny": "function",
        "jcc": "function",
        "jcs": "function",
        "jeq": "function",
        "jmi": "function",
        "jmp": "function",
        "jne": "function",
        "jpl": "function",
        "jsr": "function",
        "jvc": "function",
        "jvs": "function",
        "lda": "function",
        "ldx": "function",
        "ldy": "function",
        "lsr": "function",
        "mva": "function",
        "mvx": "function",
        "mvy": "function",
        "mwa": "function",
        "mwx": "function",
        "mwy": "function",
        "nop": "function",
        "opt": "keyword1",
        "ora": "function",
        "org": "keyword1",
        "pha": "function",
        "php": "function",
        "pla": "function",
        "plp": "function",
        "rcc": "function",
        "rcs": "function",
        "req": "function",
        "rmi": "function",
        "rne": "function",
        "rol": "function",
        "ror": "function",
        "rpl": "function",
        "rti": "function",
        "rts": "function",
        "run": "keyword1",
        "rvc": "function",
        "rvs": "function",
        "sbc": "function",
        "scc": "function",
        "scs": "function",
        "sec": "function",
        "sed": "function",
        "seg": "keyword1",
        "sei": "function",
        "seq": "function",
        "smi": "function",
        "sne": "function",
        "spl": "function",
        "sta": "function",
        "stx": "function",
        "sty": "function",
        "sub": "function",
        "svc": "function",
        "svs": "function",
        "tax": "function",
        "tay": "function",
        "tsx": "function",
        "txa": "function",
        "txs": "function",
        "tya": "function",
        "x": "keyword3",
        "y": "keyword3",
}

# Dictionary of keywords dictionaries for assembly_6502 mode.
keywordsDictDict = {
        "assembly_6502_main": assembly_6502_main_keywords_dict,
}

# Rules for assembly_6502_main ruleset.

def assembly_6502_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";")

def assembly_6502_rule1(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
          no_line_break=True)

def assembly_6502_rule2(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
          no_line_break=True)

def assembly_6502_rule3(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern=" ",
          at_whitespace_end=True,
          exclude_match=True)

def assembly_6502_rule4(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="label", pattern="\t",
          at_whitespace_end=True,
          exclude_match=True)

def assembly_6502_rule5(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="digit", pattern="$",
          exclude_match=True)

def assembly_6502_rule6(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="digit", pattern="#",
          exclude_match=True)

def assembly_6502_rule7(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="+")

def assembly_6502_rule8(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="-")

def assembly_6502_rule9(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="/")

def assembly_6502_rule10(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="*")

def assembly_6502_rule11(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="%")

def assembly_6502_rule12(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="|")

def assembly_6502_rule13(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="^")

def assembly_6502_rule14(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&")

def assembly_6502_rule15(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="~")

def assembly_6502_rule16(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!")

def assembly_6502_rule17(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="=")

def assembly_6502_rule18(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<")

def assembly_6502_rule19(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">")

def assembly_6502_rule20(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<<")

def assembly_6502_rule21(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">>")

def assembly_6502_rule22(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<>")

def assembly_6502_rule23(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="==")

def assembly_6502_rule24(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="!=")

def assembly_6502_rule25(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="<=")

def assembly_6502_rule26(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq=">=")

def assembly_6502_rule27(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="&&")

def assembly_6502_rule28(colorer, s, i):
    return colorer.match_plain_seq(s, i, kind="operator", seq="||")

def assembly_6502_rule29(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for assembly_6502_main ruleset.
rulesDict1 = {
        "\t": [assembly_6502_rule4,],
        " ": [assembly_6502_rule3,],
        "!": [assembly_6502_rule16, assembly_6502_rule24,],
        "\"": [assembly_6502_rule2,],
        "#": [assembly_6502_rule6,],
        "$": [assembly_6502_rule5,],
        "%": [assembly_6502_rule11,],
        "&": [assembly_6502_rule14, assembly_6502_rule27,],
        "'": [assembly_6502_rule1,],
        "*": [assembly_6502_rule10,],
        "+": [assembly_6502_rule7,],
        "-": [assembly_6502_rule8,],
        "/": [assembly_6502_rule9,],
        "0": [assembly_6502_rule29,],
        "1": [assembly_6502_rule29,],
        "2": [assembly_6502_rule29,],
        "3": [assembly_6502_rule29,],
        "4": [assembly_6502_rule29,],
        "5": [assembly_6502_rule29,],
        "6": [assembly_6502_rule29,],
        "7": [assembly_6502_rule29,],
        "8": [assembly_6502_rule29,],
        "9": [assembly_6502_rule29,],
        ";": [assembly_6502_rule0,],
        "<": [assembly_6502_rule18, assembly_6502_rule20, assembly_6502_rule22, assembly_6502_rule25,],
        "=": [assembly_6502_rule17, assembly_6502_rule23,],
        ">": [assembly_6502_rule19, assembly_6502_rule21, assembly_6502_rule26,],
        "@": [assembly_6502_rule29,],
        "A": [assembly_6502_rule29,],
        "B": [assembly_6502_rule29,],
        "C": [assembly_6502_rule29,],
        "D": [assembly_6502_rule29,],
        "E": [assembly_6502_rule29,],
        "F": [assembly_6502_rule29,],
        "G": [assembly_6502_rule29,],
        "H": [assembly_6502_rule29,],
        "I": [assembly_6502_rule29,],
        "J": [assembly_6502_rule29,],
        "K": [assembly_6502_rule29,],
        "L": [assembly_6502_rule29,],
        "M": [assembly_6502_rule29,],
        "N": [assembly_6502_rule29,],
        "O": [assembly_6502_rule29,],
        "P": [assembly_6502_rule29,],
        "Q": [assembly_6502_rule29,],
        "R": [assembly_6502_rule29,],
        "S": [assembly_6502_rule29,],
        "T": [assembly_6502_rule29,],
        "U": [assembly_6502_rule29,],
        "V": [assembly_6502_rule29,],
        "W": [assembly_6502_rule29,],
        "X": [assembly_6502_rule29,],
        "Y": [assembly_6502_rule29,],
        "Z": [assembly_6502_rule29,],
        "^": [assembly_6502_rule13,],
        "a": [assembly_6502_rule29,],
        "b": [assembly_6502_rule29,],
        "c": [assembly_6502_rule29,],
        "d": [assembly_6502_rule29,],
        "e": [assembly_6502_rule29,],
        "f": [assembly_6502_rule29,],
        "g": [assembly_6502_rule29,],
        "h": [assembly_6502_rule29,],
        "i": [assembly_6502_rule29,],
        "j": [assembly_6502_rule29,],
        "k": [assembly_6502_rule29,],
        "l": [assembly_6502_rule29,],
        "m": [assembly_6502_rule29,],
        "n": [assembly_6502_rule29,],
        "o": [assembly_6502_rule29,],
        "p": [assembly_6502_rule29,],
        "q": [assembly_6502_rule29,],
        "r": [assembly_6502_rule29,],
        "s": [assembly_6502_rule29,],
        "t": [assembly_6502_rule29,],
        "u": [assembly_6502_rule29,],
        "v": [assembly_6502_rule29,],
        "w": [assembly_6502_rule29,],
        "x": [assembly_6502_rule29,],
        "y": [assembly_6502_rule29,],
        "z": [assembly_6502_rule29,],
        "|": [assembly_6502_rule12, assembly_6502_rule28,],
        "~": [assembly_6502_rule15,],
}

# x.rulesDictDict for assembly_6502 mode.
rulesDictDict = {
        "assembly_6502_main": rulesDict1,
}

# Import dict for assembly_6502 mode.
importDict = {}
