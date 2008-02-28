# Leo colorizer control file for doxygen mode.
# This file is in the public domain.

# Properties for doxygen mode.
properties = {
	"lineComment": "#",
}

# Attributes dict for doxygen_main ruleset.
doxygen_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "\\",
	"highlight_digits": "true",
	"ignore_case": "false",
	"no_word_sep": "",
}

# Attributes dict for doxygen_doxygen ruleset.
doxygen_doxygen_attributes_dict = {
	"default": "COMMENT3",
	"digit_re": "",
	"escape": "\\",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "",
}

# Dictionary of attributes dictionaries for doxygen mode.
attributesDictDict = {
	"doxygen_doxygen": doxygen_doxygen_attributes_dict,
	"doxygen_main": doxygen_main_attributes_dict,
}

# Keywords dict for doxygen_main ruleset.
doxygen_main_keywords_dict = {
	"NO": "keyword3",
	"YES": "keyword2",
}

# Keywords dict for doxygen_doxygen ruleset.
doxygen_doxygen_keywords_dict = {
	"&": "label",
	"<": "label",
	">": "label",
	"@": "label",
	"@#": "label",
	"@$": "label",
	"@%": "label",
	"@@": "label",
	"@\\": "label",
	"@a": "label",
	"@addindex": "label",
	"@addtogroup": "label",
	"@anchor": "label",
	"@arg": "label",
	"@attention": "label",
	"@author": "label",
	"@b": "label",
	"@brief": "label",
	"@bug": "label",
	"@c": "label",
	"@callgraph": "label",
	"@category": "label",
	"@class": "label",
	"@code": "label",
	"@copydoc": "label",
	"@date": "label",
	"@def": "label",
	"@defgroup": "label",
	"@deprecated": "label",
	"@dontinclude": "label",
	"@dot": "label",
	"@dotfile": "label",
	"@e": "label",
	"@else": "label",
	"@elseif": "label",
	"@em": "label",
	"@endcode": "label",
	"@enddot": "label",
	"@endhtmlonly": "label",
	"@endif": "label",
	"@endlatexonly": "label",
	"@endlink": "label",
	"@endmanonly": "label",
	"@endverbatim": "label",
	"@endxmlonly": "label",
	"@enum": "label",
	"@example": "label",
	"@exception": "label",
	"@f$": "label",
	"@f[": "label",
	"@f]": "label",
	"@file": "label",
	"@fn": "label",
	"@hideinitializer": "label",
	"@htmlinclude": "label",
	"@htmlonly": "label",
	"@if": "label",
	"@ifnot": "label",
	"@image": "label",
	"@include": "label",
	"@includelineno": "label",
	"@ingroup": "label",
	"@interface": "label",
	"@internal": "label",
	"@invariant": "label",
	"@latexonly": "label",
	"@li": "label",
	"@line": "label",
	"@link": "label",
	"@mainpage": "label",
	"@manonly": "label",
	"@n": "label",
	"@name": "label",
	"@namespace": "label",
	"@nosubgrouping": "label",
	"@note": "label",
	"@overload": "label",
	"@p": "label",
	"@package": "label",
	"@page": "label",
	"@par": "label",
	"@paragraph": "label",
	"@param": "label",
	"@param[in,out]": "label",
	"@param[in]": "label",
	"@param[out]": "label",
	"@post": "label",
	"@pre": "label",
	"@private": "label",
	"@privatesection": "label",
	"@property": "label",
	"@protected": "label",
	"@protectedsection": "label",
	"@protocol": "label",
	"@public": "label",
	"@publicsection": "label",
	"@ref": "label",
	"@relates": "label",
	"@relatesalso": "label",
	"@remarks": "label",
	"@return": "label",
	"@retval": "label",
	"@sa": "label",
	"@section": "label",
	"@showinitializer": "label",
	"@since": "label",
	"@skip": "label",
	"@skipline": "label",
	"@struct": "label",
	"@subsection": "label",
	"@subsubsection": "label",
	"@test": "label",
	"@throw": "label",
	"@todo": "label",
	"@typedef": "label",
	"@union": "label",
	"@until": "label",
	"@var": "label",
	"@verbatim": "label",
	"@verbinclude": "label",
	"@version": "label",
	"@warning": "label",
	"@weakgroup": "label",
	"@xmlonly": "label",
	"@xrefitem": "label",
	"@~": "label",
	"\\": "label",
	"\\#": "label",
	"\\$": "label",
	"\\%": "label",
	"\\@": "label",
	"\\\\": "label",
	"\\a": "label",
	"\\addindex": "label",
	"\\addtogroup": "label",
	"\\anchor": "label",
	"\\arg": "label",
	"\\attention": "label",
	"\\author": "label",
	"\\b": "label",
	"\\brief": "label",
	"\\bug": "label",
	"\\c": "label",
	"\\callgraph": "label",
	"\\category": "label",
	"\\class": "label",
	"\\code": "label",
	"\\copydoc": "label",
	"\\date": "label",
	"\\def": "label",
	"\\defgroup": "label",
	"\\deprecated": "label",
	"\\dontinclude": "label",
	"\\dot": "label",
	"\\dotfile": "label",
	"\\e": "label",
	"\\else": "label",
	"\\elseif": "label",
	"\\em": "label",
	"\\endcode": "label",
	"\\enddot": "label",
	"\\endhtmlonly": "label",
	"\\endif": "label",
	"\\endlatexonly": "label",
	"\\endlink": "label",
	"\\endmanonly": "label",
	"\\endverbatim": "label",
	"\\endxmlonly": "label",
	"\\enum": "label",
	"\\example": "label",
	"\\exception": "label",
	"\\f$": "label",
	"\\f[": "label",
	"\\f]": "label",
	"\\file": "label",
	"\\fn": "label",
	"\\hideinitializer": "label",
	"\\htmlinclude": "label",
	"\\htmlonly": "label",
	"\\if": "label",
	"\\ifnot": "label",
	"\\image": "label",
	"\\include": "label",
	"\\includelineno": "label",
	"\\ingroup": "label",
	"\\interface": "label",
	"\\internal": "label",
	"\\invariant": "label",
	"\\latexonly": "label",
	"\\li": "label",
	"\\line": "label",
	"\\link": "label",
	"\\mainpage": "label",
	"\\manonly": "label",
	"\\n": "label",
	"\\name": "label",
	"\\namespace": "label",
	"\\nosubgrouping": "label",
	"\\note": "label",
	"\\overload": "label",
	"\\p": "label",
	"\\package": "label",
	"\\page": "label",
	"\\par": "label",
	"\\paragraph": "label",
	"\\param": "label",
	"\\param[in,out]": "label",
	"\\param[in]": "label",
	"\\param[out]": "label",
	"\\post": "label",
	"\\pre": "label",
	"\\private": "label",
	"\\privatesection": "label",
	"\\property": "label",
	"\\protected": "label",
	"\\protectedsection": "label",
	"\\protocol": "label",
	"\\public": "label",
	"\\publicsection": "label",
	"\\ref": "label",
	"\\relates": "label",
	"\\relatesalso": "label",
	"\\remarks": "label",
	"\\return": "label",
	"\\retval": "label",
	"\\sa": "label",
	"\\section": "label",
	"\\showinitializer": "label",
	"\\since": "label",
	"\\skip": "label",
	"\\skipline": "label",
	"\\struct": "label",
	"\\subsection": "label",
	"\\subsubsection": "label",
	"\\test": "label",
	"\\throw": "label",
	"\\todo": "label",
	"\\typedef": "label",
	"\\union": "label",
	"\\until": "label",
	"\\var": "label",
	"\\verbatim": "label",
	"\\verbinclude": "label",
	"\\version": "label",
	"\\warning": "label",
	"\\weakgroup": "label",
	"\\xmlonly": "label",
	"\\xrefitem": "label",
	"\\~": "label",
}

# Dictionary of keywords dictionaries for doxygen mode.
keywordsDictDict = {
	"doxygen_doxygen": doxygen_doxygen_keywords_dict,
	"doxygen_main": doxygen_main_keywords_dict,
}

# Rules for doxygen_main ruleset.

def doxygen_rule0(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq="#",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def doxygen_rule1(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="keyword1", pattern="=",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, exclude_match=True)

def doxygen_rule2(colorer, s, i):
    return colorer.match_mark_previous(s, i, kind="keyword1", pattern="+=",
        at_line_start=True, at_whitespace_end=False, at_word_start=False, exclude_match=True)

def doxygen_rule3(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="\"", end="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def doxygen_rule4(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="'", end="'",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def doxygen_rule5(colorer, s, i):
    return colorer.match_span(s, i, kind="literal1", begin="`", end="`",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def doxygen_rule6(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for doxygen_main ruleset.
rulesDict1 = {
	"\"": [doxygen_rule3,],
	"#": [doxygen_rule0,doxygen_rule6,],
	"$": [doxygen_rule6,],
	"%": [doxygen_rule6,],
	"&": [doxygen_rule6,],
	"'": [doxygen_rule4,],
	"+": [doxygen_rule2,],
	",": [doxygen_rule6,],
	"0": [doxygen_rule6,],
	"1": [doxygen_rule6,],
	"2": [doxygen_rule6,],
	"3": [doxygen_rule6,],
	"4": [doxygen_rule6,],
	"5": [doxygen_rule6,],
	"6": [doxygen_rule6,],
	"7": [doxygen_rule6,],
	"8": [doxygen_rule6,],
	"9": [doxygen_rule6,],
	"<": [doxygen_rule6,],
	"=": [doxygen_rule1,],
	">": [doxygen_rule6,],
	"@": [doxygen_rule6,],
	"A": [doxygen_rule6,],
	"B": [doxygen_rule6,],
	"C": [doxygen_rule6,],
	"D": [doxygen_rule6,],
	"E": [doxygen_rule6,],
	"F": [doxygen_rule6,],
	"G": [doxygen_rule6,],
	"H": [doxygen_rule6,],
	"I": [doxygen_rule6,],
	"J": [doxygen_rule6,],
	"K": [doxygen_rule6,],
	"L": [doxygen_rule6,],
	"M": [doxygen_rule6,],
	"N": [doxygen_rule6,],
	"O": [doxygen_rule6,],
	"P": [doxygen_rule6,],
	"Q": [doxygen_rule6,],
	"R": [doxygen_rule6,],
	"S": [doxygen_rule6,],
	"T": [doxygen_rule6,],
	"U": [doxygen_rule6,],
	"V": [doxygen_rule6,],
	"W": [doxygen_rule6,],
	"X": [doxygen_rule6,],
	"Y": [doxygen_rule6,],
	"Z": [doxygen_rule6,],
	"[": [doxygen_rule6,],
	"\\": [doxygen_rule6,],
	"]": [doxygen_rule6,],
	"`": [doxygen_rule5,],
	"a": [doxygen_rule6,],
	"b": [doxygen_rule6,],
	"c": [doxygen_rule6,],
	"d": [doxygen_rule6,],
	"e": [doxygen_rule6,],
	"f": [doxygen_rule6,],
	"g": [doxygen_rule6,],
	"h": [doxygen_rule6,],
	"i": [doxygen_rule6,],
	"j": [doxygen_rule6,],
	"k": [doxygen_rule6,],
	"l": [doxygen_rule6,],
	"m": [doxygen_rule6,],
	"n": [doxygen_rule6,],
	"o": [doxygen_rule6,],
	"p": [doxygen_rule6,],
	"q": [doxygen_rule6,],
	"r": [doxygen_rule6,],
	"s": [doxygen_rule6,],
	"t": [doxygen_rule6,],
	"u": [doxygen_rule6,],
	"v": [doxygen_rule6,],
	"w": [doxygen_rule6,],
	"x": [doxygen_rule6,],
	"y": [doxygen_rule6,],
	"z": [doxygen_rule6,],
	"~": [doxygen_rule6,],
}

# Rules for doxygen_doxygen ruleset.

def doxygen_rule7(colorer, s, i):
    return colorer.match_seq(s, i, kind="comment3", seq="*",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def doxygen_rule8(colorer, s, i):
    return colorer.match_span(s, i, kind="comment1", begin="<!--", end="-->",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="",exclude_match=False,
        no_escape=False, no_line_break=False, no_word_break=False)

def doxygen_rule9(colorer, s, i):
    return colorer.match_seq(s, i, kind="comment3", seq="<<",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def doxygen_rule10(colorer, s, i):
    return colorer.match_seq(s, i, kind="comment3", seq="<=",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def doxygen_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="comment3", seq="< ",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def doxygen_rule12(colorer, s, i):
    return colorer.match_span(s, i, kind="markup", begin="<", end=">",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="xml::tags",exclude_match=False,
        no_escape=False, no_line_break=True, no_word_break=False)

def doxygen_rule13(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for doxygen_doxygen ruleset.
rulesDict2 = {
	"#": [doxygen_rule13,],
	"$": [doxygen_rule13,],
	"%": [doxygen_rule13,],
	"&": [doxygen_rule13,],
	"*": [doxygen_rule7,],
	",": [doxygen_rule13,],
	"0": [doxygen_rule13,],
	"1": [doxygen_rule13,],
	"2": [doxygen_rule13,],
	"3": [doxygen_rule13,],
	"4": [doxygen_rule13,],
	"5": [doxygen_rule13,],
	"6": [doxygen_rule13,],
	"7": [doxygen_rule13,],
	"8": [doxygen_rule13,],
	"9": [doxygen_rule13,],
	"<": [doxygen_rule8,doxygen_rule9,doxygen_rule10,doxygen_rule11,doxygen_rule12,doxygen_rule13,],
	">": [doxygen_rule13,],
	"@": [doxygen_rule13,],
	"A": [doxygen_rule13,],
	"B": [doxygen_rule13,],
	"C": [doxygen_rule13,],
	"D": [doxygen_rule13,],
	"E": [doxygen_rule13,],
	"F": [doxygen_rule13,],
	"G": [doxygen_rule13,],
	"H": [doxygen_rule13,],
	"I": [doxygen_rule13,],
	"J": [doxygen_rule13,],
	"K": [doxygen_rule13,],
	"L": [doxygen_rule13,],
	"M": [doxygen_rule13,],
	"N": [doxygen_rule13,],
	"O": [doxygen_rule13,],
	"P": [doxygen_rule13,],
	"Q": [doxygen_rule13,],
	"R": [doxygen_rule13,],
	"S": [doxygen_rule13,],
	"T": [doxygen_rule13,],
	"U": [doxygen_rule13,],
	"V": [doxygen_rule13,],
	"W": [doxygen_rule13,],
	"X": [doxygen_rule13,],
	"Y": [doxygen_rule13,],
	"Z": [doxygen_rule13,],
	"[": [doxygen_rule13,],
	"\\": [doxygen_rule13,],
	"]": [doxygen_rule13,],
	"a": [doxygen_rule13,],
	"b": [doxygen_rule13,],
	"c": [doxygen_rule13,],
	"d": [doxygen_rule13,],
	"e": [doxygen_rule13,],
	"f": [doxygen_rule13,],
	"g": [doxygen_rule13,],
	"h": [doxygen_rule13,],
	"i": [doxygen_rule13,],
	"j": [doxygen_rule13,],
	"k": [doxygen_rule13,],
	"l": [doxygen_rule13,],
	"m": [doxygen_rule13,],
	"n": [doxygen_rule13,],
	"o": [doxygen_rule13,],
	"p": [doxygen_rule13,],
	"q": [doxygen_rule13,],
	"r": [doxygen_rule13,],
	"s": [doxygen_rule13,],
	"t": [doxygen_rule13,],
	"u": [doxygen_rule13,],
	"v": [doxygen_rule13,],
	"w": [doxygen_rule13,],
	"x": [doxygen_rule13,],
	"y": [doxygen_rule13,],
	"z": [doxygen_rule13,],
	"~": [doxygen_rule13,],
}

# x.rulesDictDict for doxygen mode.
rulesDictDict = {
	"doxygen_doxygen": rulesDict2,
	"doxygen_main": rulesDict1,
}

# Import dict for doxygen mode.
importDict = {}

