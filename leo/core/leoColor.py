#@+leo-ver=4-thin
#@+node:ekr.20031218072017.2794:@thin leoColor.py
#@<< docstring >>
#@+node:bob.20080115083029:<< docstring >>
"""Syntax coloring routines and color database for Leo.


In addition to syntax coloring routines, this module also
contains a color database and accessor functions.

leo_color_database is a dictionary of color names mapped onto the
colors '#rrggbb' representation.

The color names are derived from standard Linux color names which
includes all Tk color names.

The names have been normalized by excluding spaces and removing
capitalization. This should also be done for all new colors.

Accessor functions are provided which will normalize name requests
before looking them up in the database.

These are:
    + getColor (aka: get)
    + getColorRGB (aka: getRGB)
    + getColorCairo (aka: getCairo)

It is recommened that these functions should be used thus:

    import leo.core.leoColor as leoColor    
    leoColor.getRGB(name, default)

rather than:

    from leoColor import getRGB
    ....

If neither 'name' nor 'default' can be translated then accessor functions
will return None.
"""
#@-node:bob.20080115083029:<< docstring >>
#@nl
#@@language python
#@@tabwidth -4
#@@pagewidth 70

import leo.core.leoGlobals as g
import re
import string

#@<< changelog >>
#@+node:bob.20080115090639:<< changelog >>
#@+at
# plumloco:
#     added < <docstring>> and < <changelog>>
#     added leo_color_database and its accessor functions
# 
#@-at
#@-node:bob.20080115090639:<< changelog >>
#@nl

# php_re = re.compile("<?(\s|=|[pP][hH][pP])")
php_re = re.compile("<?(\s[pP][hH][pP])")

#@<< define colorizer constants >>
#@+node:ekr.20031218072017.2795:<< define colorizer constants >>
# These defaults are sure to exist.
default_colors_dict = {
    # tag name       :(     option name,           default color),
    "comment"        :("comment_color",               "red"),
    "cwebName"       :("cweb_section_name_color",     "red"),
    "pp"             :("directive_color",             "blue"),
    "docPart"        :("doc_part_color",              "red"),
    "keyword"        :("keyword_color",               "blue"),
    "leoKeyword"     :("leo_keyword_color",           "blue"),
    "link"           :("section_name_color",          "red"),
    "nameBrackets"   :("section_name_brackets_color", "blue"),
    "string"         :("string_color",                "#00aa00"), # Used by IDLE.
    "name"           :("undefined_section_name_color","red"),
    "latexBackground":("latex_background_color","white"),
}

default_font_dict = {
    # tag name       : option name
    'comment'        :'comment_font',
    'cwebName'       :'cweb_section_name_font',
    'pp'             :'directive_font',
    'docPart'        :'doc_part_font',
    'keyword'        :'keyword_font',
    'leoKeyword'     :'leo_keyword_font',
    'link'           :'section_name_font',
    'nameBrackets'   :'section_name_brackets_font',
    'string'         :'string_font',
    'name'           :'undefined_section_name_font',
    'latexBackground':'latex_background_font',
}
#@-node:ekr.20031218072017.2795:<< define colorizer constants >>
#@nl
#@<< define global colorizer data >>
#@+node:EKR.20040623090054:<< define global colorizer data >>
case_insensitiveLanguages = ['plsql',]
#@-node:EKR.20040623090054:<< define global colorizer data >>
#@nl
#@<< define leo_color_database >>
#@+node:bob.20080115070511.2:<< define leo_color_database >>
#@+at
# All names added to this database should be in normalized form,
# otherwise the accessor functions won't work.
# 
# Adding names here will make them availiable to all gui's and
# dhtml that use this service.
# 
# Names are normalized by removing spaces and capitalization.
#@-at
#@@c

leo_color_database = {

    # leo colors
    "leoblue": "#F0F8FF", #alice blue
    "leoyellow": "#ffffec",
    "leopink":  "#FFE4E1", # misty rose

    "aliceblue": "#F0F8FF",
    "antiquewhite": "#FAEBD7",
    "antiquewhite1": "#FFEFDB",
    "antiquewhite2": "#EEDFCC",
    "antiquewhite3": "#CDC0B0",
    "antiquewhite4": "#8B8378",
    "aquamarine": "#7FFFD4",
    "aquamarine1": "#7FFFD4",
    "aquamarine2": "#76EEC6",
    "aquamarine3": "#66CDAA",
    "aquamarine4": "#458B74",
    "azure": "#F0FFFF",
    "azure1": "#F0FFFF",
    "azure2": "#E0EEEE",
    "azure3": "#C1CDCD",
    "azure4": "#838B8B",
    "beige": "#F5F5DC",
    "bisque": "#FFE4C4",
    "bisque1": "#FFE4C4",
    "bisque2": "#EED5B7",
    "bisque3": "#CDB79E",
    "bisque4": "#8B7D6B",
    "black": "#000000",
    "blanchedalmond": "#FFEBCD",
    "blue": "#0000FF",
    "blue1": "#0000FF",
    "blue2": "#0000EE",
    "blue3": "#0000CD",
    "blue4": "#00008B",
    "blueviolet": "#8A2BE2",
    "brown": "#A52A2A",
    "brown1": "#FF4040",
    "brown2": "#EE3B3B",
    "brown3": "#CD3333",
    "brown4": "#8B2323",
    "burlywood": "#DEB887",
    "burlywood1": "#FFD39B",
    "burlywood2": "#EEC591",
    "burlywood3": "#CDAA7D",
    "burlywood4": "#8B7355",
    "cadetblue": "#5F9EA0",
    "cadetblue1": "#98F5FF",
    "cadetblue2": "#8EE5EE",
    "cadetblue3": "#7AC5CD",
    "cadetblue4": "#53868B",
    "chartreuse": "#7FFF00",
    "chartreuse1": "#7FFF00",
    "chartreuse2": "#76EE00",
    "chartreuse3": "#66CD00",
    "chartreuse4": "#458B00",
    "chocolate": "#D2691E",
    "chocolate1": "#FF7F24",
    "chocolate2": "#EE7621",
    "chocolate3": "#CD661D",
    "chocolate4": "#8B4513",
    "coral": "#FF7F50",
    "coral1": "#FF7256",
    "coral2": "#EE6A50",
    "coral3": "#CD5B45",
    "coral4": "#8B3E2F",
    "cornflowerblue": "#6495ED",
    "cornsilk": "#FFF8DC",
    "cornsilk1": "#FFF8DC",
    "cornsilk2": "#EEE8CD",
    "cornsilk3": "#CDC8B1",
    "cornsilk4": "#8B8878",
    "cyan": "#00FFFF",
    "cyan1": "#00FFFF",
    "cyan2": "#00EEEE",
    "cyan3": "#00CDCD",
    "cyan4": "#008B8B",
    "darkblue": "#00008B",
    "darkcyan": "#008B8B",
    "darkgoldenrod": "#B8860B",
    "darkgoldenrod1": "#FFB90F",
    "darkgoldenrod2": "#EEAD0E",
    "darkgoldenrod3": "#CD950C",
    "darkgoldenrod4": "#8B6508",
    "darkgray": "#A9A9A9",
    "darkgreen": "#006400",
    "darkgrey": "#A9A9A9",
    "darkkhaki": "#BDB76B",
    "darkmagenta": "#8B008B",
    "darkolivegreen": "#556B2F",
    "darkolivegreen1": "#CAFF70",
    "darkolivegreen2": "#BCEE68",
    "darkolivegreen3": "#A2CD5A",
    "darkolivegreen4": "#6E8B3D",
    "darkorange": "#FF8C00",
    "darkorange1": "#FF7F00",
    "darkorange2": "#EE7600",
    "darkorange3": "#CD6600",
    "darkorange4": "#8B4500",
    "darkorchid": "#9932CC",
    "darkorchid1": "#BF3EFF",
    "darkorchid2": "#B23AEE",
    "darkorchid3": "#9A32CD",
    "darkorchid4": "#68228B",
    "darkred": "#8B0000",
    "darksalmon": "#E9967A",
    "darkseagreen": "#8FBC8F",
    "darkseagreen1": "#C1FFC1",
    "darkseagreen2": "#B4EEB4",
    "darkseagreen3": "#9BCD9B",
    "darkseagreen4": "#698B69",
    "darkslateblue": "#483D8B",
    "darkslategray": "#2F4F4F",
    "darkslategray1": "#97FFFF",
    "darkslategray2": "#8DEEEE",
    "darkslategray3": "#79CDCD",
    "darkslategray4": "#528B8B",
    "darkslategrey": "#2F4F4F",
    "darkturquoise": "#00CED1",
    "darkviolet": "#9400D3",
    "deeppink": "#FF1493",
    "deeppink1": "#FF1493",
    "deeppink2": "#EE1289",
    "deeppink3": "#CD1076",
    "deeppink4": "#8B0A50",
    "deepskyblue": "#00BFFF",
    "deepskyblue1": "#00BFFF",
    "deepskyblue2": "#00B2EE",
    "deepskyblue3": "#009ACD",
    "deepskyblue4": "#00688B",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1E90FF",
    "dodgerblue1": "#1E90FF",
    "dodgerblue2": "#1C86EE",
    "dodgerblue3": "#1874CD",
    "dodgerblue4": "#104E8B",
    "firebrick": "#B22222",
    "firebrick1": "#FF3030",
    "firebrick2": "#EE2C2C",
    "firebrick3": "#CD2626",
    "firebrick4": "#8B1A1A",
    "floralwhite": "#FFFAF0",
    "forestgreen": "#228B22",
    "gainsboro": "#DCDCDC",
    "ghostwhite": "#F8F8FF",
    "gold": "#FFD700",
    "gold1": "#FFD700",
    "gold2": "#EEC900",
    "gold3": "#CDAD00",
    "gold4": "#8B7500",
    "goldenrod": "#DAA520",
    "goldenrod1": "#FFC125",
    "goldenrod2": "#EEB422",
    "goldenrod3": "#CD9B1D",
    "goldenrod4": "#8B6914",
    "gray": "#BEBEBE",
    "gray0": "#000000",
    "gray1": "#030303",
    "gray10": "#1A1A1A",
    "gray100": "#FFFFFF",
    "gray11": "#1C1C1C",
    "gray12": "#1F1F1F",
    "gray13": "#212121",
    "gray14": "#242424",
    "gray15": "#262626",
    "gray16": "#292929",
    "gray17": "#2B2B2B",
    "gray18": "#2E2E2E",
    "gray19": "#303030",
    "gray2": "#050505",
    "gray20": "#333333",
    "gray21": "#363636",
    "gray22": "#383838",
    "gray23": "#3B3B3B",
    "gray24": "#3D3D3D",
    "gray25": "#404040",
    "gray26": "#424242",
    "gray27": "#454545",
    "gray28": "#474747",
    "gray29": "#4A4A4A",
    "gray3": "#080808",
    "gray30": "#4D4D4D",
    "gray31": "#4F4F4F",
    "gray32": "#525252",
    "gray33": "#545454",
    "gray34": "#575757",
    "gray35": "#595959",
    "gray36": "#5C5C5C",
    "gray37": "#5E5E5E",
    "gray38": "#616161",
    "gray39": "#636363",
    "gray4": "#0A0A0A",
    "gray40": "#666666",
    "gray41": "#696969",
    "gray42": "#6B6B6B",
    "gray43": "#6E6E6E",
    "gray44": "#707070",
    "gray45": "#737373",
    "gray46": "#757575",
    "gray47": "#787878",
    "gray48": "#7A7A7A",
    "gray49": "#7D7D7D",
    "gray5": "#0D0D0D",
    "gray50": "#7F7F7F",
    "gray51": "#828282",
    "gray52": "#858585",
    "gray53": "#878787",
    "gray54": "#8A8A8A",
    "gray55": "#8C8C8C",
    "gray56": "#8F8F8F",
    "gray57": "#919191",
    "gray58": "#949494",
    "gray59": "#969696",
    "gray6": "#0F0F0F",
    "gray60": "#999999",
    "gray61": "#9C9C9C",
    "gray62": "#9E9E9E",
    "gray63": "#A1A1A1",
    "gray64": "#A3A3A3",
    "gray65": "#A6A6A6",
    "gray66": "#A8A8A8",
    "gray67": "#ABABAB",
    "gray68": "#ADADAD",
    "gray69": "#B0B0B0",
    "gray7": "#121212",
    "gray70": "#B3B3B3",
    "gray71": "#B5B5B5",
    "gray72": "#B8B8B8",
    "gray73": "#BABABA",
    "gray74": "#BDBDBD",
    "gray75": "#BFBFBF",
    "gray76": "#C2C2C2",
    "gray77": "#C4C4C4",
    "gray78": "#C7C7C7",
    "gray79": "#C9C9C9",
    "gray8": "#141414",
    "gray80": "#CCCCCC",
    "gray81": "#CFCFCF",
    "gray82": "#D1D1D1",
    "gray83": "#D4D4D4",
    "gray84": "#D6D6D6",
    "gray85": "#D9D9D9",
    "gray86": "#DBDBDB",
    "gray87": "#DEDEDE",
    "gray88": "#E0E0E0",
    "gray89": "#E3E3E3",
    "gray9": "#171717",
    "gray90": "#E5E5E5",
    "gray91": "#E8E8E8",
    "gray92": "#EBEBEB",
    "gray93": "#EDEDED",
    "gray94": "#F0F0F0",
    "gray95": "#F2F2F2",
    "gray96": "#F5F5F5",
    "gray97": "#F7F7F7",
    "gray98": "#FAFAFA",
    "gray99": "#FCFCFC",
    "green": "#00FF00",
    "green1": "#00FF00",
    "green2": "#00EE00",
    "green3": "#00CD00",
    "green4": "#008B00",
    "greenyellow": "#ADFF2F",
    "grey": "#BEBEBE",
    "grey0": "#000000",
    "grey1": "#030303",
    "grey10": "#1A1A1A",
    "grey100": "#FFFFFF",
    "grey11": "#1C1C1C",
    "grey12": "#1F1F1F",
    "grey13": "#212121",
    "grey14": "#242424",
    "grey15": "#262626",
    "grey16": "#292929",
    "grey17": "#2B2B2B",
    "grey18": "#2E2E2E",
    "grey19": "#303030",
    "grey2": "#050505",
    "grey20": "#333333",
    "grey21": "#363636",
    "grey22": "#383838",
    "grey23": "#3B3B3B",
    "grey24": "#3D3D3D",
    "grey25": "#404040",
    "grey26": "#424242",
    "grey27": "#454545",
    "grey28": "#474747",
    "grey29": "#4A4A4A",
    "grey3": "#080808",
    "grey30": "#4D4D4D",
    "grey31": "#4F4F4F",
    "grey32": "#525252",
    "grey33": "#545454",
    "grey34": "#575757",
    "grey35": "#595959",
    "grey36": "#5C5C5C",
    "grey37": "#5E5E5E",
    "grey38": "#616161",
    "grey39": "#636363",
    "grey4": "#0A0A0A",
    "grey40": "#666666",
    "grey41": "#696969",
    "grey42": "#6B6B6B",
    "grey43": "#6E6E6E",
    "grey44": "#707070",
    "grey45": "#737373",
    "grey46": "#757575",
    "grey47": "#787878",
    "grey48": "#7A7A7A",
    "grey49": "#7D7D7D",
    "grey5": "#0D0D0D",
    "grey50": "#7F7F7F",
    "grey51": "#828282",
    "grey52": "#858585",
    "grey53": "#878787",
    "grey54": "#8A8A8A",
    "grey55": "#8C8C8C",
    "grey56": "#8F8F8F",
    "grey57": "#919191",
    "grey58": "#949494",
    "grey59": "#969696",
    "grey6": "#0F0F0F",
    "grey60": "#999999",
    "grey61": "#9C9C9C",
    "grey62": "#9E9E9E",
    "grey63": "#A1A1A1",
    "grey64": "#A3A3A3",
    "grey65": "#A6A6A6",
    "grey66": "#A8A8A8",
    "grey67": "#ABABAB",
    "grey68": "#ADADAD",
    "grey69": "#B0B0B0",
    "grey7": "#121212",
    "grey70": "#B3B3B3",
    "grey71": "#B5B5B5",
    "grey72": "#B8B8B8",
    "grey73": "#BABABA",
    "grey74": "#BDBDBD",
    "grey75": "#BFBFBF",
    "grey76": "#C2C2C2",
    "grey77": "#C4C4C4",
    "grey78": "#C7C7C7",
    "grey79": "#C9C9C9",
    "grey8": "#141414",
    "grey80": "#CCCCCC",
    "grey81": "#CFCFCF",
    "grey82": "#D1D1D1",
    "grey84": "#D6D6D6",
    "grey85": "#D9D9D9",
    "grey86": "#DBDBDB",
    "grey87": "#DEDEDE",
    "grey88": "#E0E0E0",
    "grey89": "#E3E3E3",
    "grey9": "#171717",
    "grey90": "#E5E5E5",
    "grey91": "#E8E8E8",
    "grey92": "#EBEBEB",
    "grey93": "#EDEDED",
    "grey94": "#F0F0F0",
    "grey95": "#F2F2F2",
    "grey96": "#F5F5F5",
    "grey97": "#F7F7F7",
    "grey98": "#FAFAFA",
    "grey99": "#FCFCFC",
    "honeydew": "#F0FFF0",
    "honeydew1": "#F0FFF0",
    "honeydew2": "#E0EEE0",
    "honeydew3": "#C1CDC1",
    "honeydew4": "#838B83",
    "hotpink": "#FF69B4",
    "hotpink1": "#FF6EB4",
    "hotpink2": "#EE6AA7",
    "hotpink3": "#CD6090",
    "hotpink4": "#8B3A62",
    "indianred": "#CD5C5C",
    "indianred1": "#FF6A6A",
    "indianred2": "#EE6363",
    "indianred3": "#CD5555",
    "indianred4": "#8B3A3A",
    "ivory": "#FFFFF0",
    "ivory1": "#FFFFF0",
    "ivory2": "#EEEEE0",
    "ivory3": "#CDCDC1",
    "ivory4": "#8B8B83",
    "khaki": "#F0E68C",
    "khaki1": "#FFF68F",
    "khaki2": "#EEE685",
    "khaki3": "#CDC673",
    "khaki4": "#8B864E",
    "lavender": "#E6E6FA",
    "lavenderblush": "#FFF0F5",
    "lavenderblush1": "#FFF0F5",
    "lavenderblush2": "#EEE0E5",
    "lavenderblush3": "#CDC1C5",
    "lavenderblush4": "#8B8386",
    "lawngreen": "#7CFC00",
    "lemonchiffon": "#FFFACD",
    "lemonchiffon1": "#FFFACD",
    "lemonchiffon2": "#EEE9BF",
    "lemonchiffon3": "#CDC9A5",
    "lemonchiffon4": "#8B8970",
    "lightblue": "#ADD8E6",
    "lightblue1": "#BFEFFF",
    "lightblue2": "#B2DFEE",
    "lightblue3": "#9AC0CD",
    "lightblue4": "#68838B",
    "lightcoral": "#F08080",
    "lightcyan": "#E0FFFF",
    "lightcyan1": "#E0FFFF",
    "lightcyan2": "#D1EEEE",
    "lightcyan3": "#B4CDCD",
    "lightcyan4": "#7A8B8B",
    "lightgoldenrod": "#EEDD82",
    "lightgoldenrod1": "#FFEC8B",
    "lightgoldenrod2": "#EEDC82",
    "lightgoldenrod3": "#CDBE70",
    "lightgoldenrod4": "#8B814C",
    "lightgoldenrodyellow": "#FAFAD2",
    "lightgray": "#D3D3D3",
    "lightgreen": "#90EE90",
    "lightgrey": "#D3D3D3",
    "lightpink": "#FFB6C1",
    "lightpink1": "#FFAEB9",
    "lightpink2": "#EEA2AD",
    "lightpink3": "#CD8C95",
    "lightpink4": "#8B5F65",
    "lightsalmon": "#FFA07A",
    "lightsalmon1": "#FFA07A",
    "lightsalmon2": "#EE9572",
    "lightsalmon3": "#CD8162",
    "lightsalmon4": "#8B5742",
    "lightseagreen": "#20B2AA",
    "lightskyblue": "#87CEFA",
    "lightskyblue1": "#B0E2FF",
    "lightskyblue2": "#A4D3EE",
    "lightskyblue3": "#8DB6CD",
    "lightskyblue4": "#607B8B",
    "lightslateblue": "#8470FF",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#B0C4DE",
    "lightsteelblue1": "#CAE1FF",
    "lightsteelblue2": "#BCD2EE",
    "lightsteelblue3": "#A2B5CD",
    "lightsteelblue4": "#6E7B8B",
    "lightyellow": "#FFFFE0",
    "lightyellow1": "#FFFFE0",
    "lightyellow2": "#EEEED1",
    "lightyellow3": "#CDCDB4",
    "lightyellow4": "#8B8B7A",
    "limegreen": "#32CD32",
    "linen": "#FAF0E6",
    "magenta": "#FF00FF",
    "magenta1": "#FF00FF",
    "magenta2": "#EE00EE",
    "magenta3": "#CD00CD",
    "magenta4": "#8B008B",
    "maroon": "#B03060",
    "maroon1": "#FF34B3",
    "maroon2": "#EE30A7",
    "maroon3": "#CD2990",
    "maroon4": "#8B1C62",
    "mediumaquamarine": "#66CDAA",
    "mediumblue": "#0000CD",
    "mediumorchid": "#BA55D3",
    "mediumorchid1": "#E066FF",
    "mediumorchid2": "#D15FEE",
    "mediumorchid3": "#B452CD",
    "mediumorchid4": "#7A378B",
    "mediumpurple": "#9370DB",
    "mediumpurple1": "#AB82FF",
    "mediumpurple2": "#9F79EE",
    "mediumpurple3": "#8968CD",
    "mediumpurple4": "#5D478B",
    "mediumseagreen": "#3CB371",
    "mediumslateblue": "#7B68EE",
    "mediumspringgreen": "#00FA9A",
    "mediumturquoise": "#48D1CC",
    "mediumvioletred": "#C71585",
    "midnightblue": "#191970",
    "mintcream": "#F5FFFA",
    "mistyrose": "#FFE4E1",
    "mistyrose1": "#FFE4E1",
    "mistyrose2": "#EED5D2",
    "mistyrose3": "#CDB7B5",
    "mistyrose4": "#8B7D7B",
    "moccasin": "#FFE4B5",
    "navajowhite": "#FFDEAD",
    "navajowhite1": "#FFDEAD",
    "navajowhite2": "#EECFA1",
    "navajowhite3": "#CDB38B",
    "navajowhite4": "#8B795E",
    "navy": "#000080",
    "navyblue": "#000080",
    "oldlace": "#FDF5E6",
    "olivedrab": "#6B8E23",
    "olivedrab1": "#C0FF3E",
    "olivedrab2": "#B3EE3A",
    "olivedrab3": "#9ACD32",
    "olivedrab4": "#698B22",
    "orange": "#FFA500",
    "orange1": "#FFA500",
    "orange2": "#EE9A00",
    "orange3": "#CD8500",
    "orange4": "#8B5A00",
    "orangered": "#FF4500",
    "orangered1": "#FF4500",
    "orangered2": "#EE4000",
    "orangered3": "#CD3700",
    "orangered4": "#8B2500",
    "orchid": "#DA70D6",
    "orchid1": "#FF83FA",
    "orchid2": "#EE7AE9",
    "orchid3": "#CD69C9",
    "orchid4": "#8B4789",
    "palegoldenrod": "#EEE8AA",
    "palegreen": "#98FB98",
    "palegreen1": "#9AFF9A",
    "palegreen2": "#90EE90",
    "palegreen3": "#7CCD7C",
    "palegreen4": "#548B54",
    "paleturquoise": "#AFEEEE",
    "paleturquoise1": "#BBFFFF",
    "paleturquoise2": "#AEEEEE",
    "paleturquoise3": "#96CDCD",
    "paleturquoise4": "#668B8B",
    "palevioletred": "#DB7093",
    "palevioletred1": "#FF82AB",
    "palevioletred2": "#EE799F",
    "palevioletred3": "#CD6889",
    "palevioletred4": "#8B475D",
    "papayawhip": "#FFEFD5",
    "peachpuff": "#FFDAB9",
    "peachpuff1": "#FFDAB9",
    "peachpuff2": "#EECBAD",
    "peachpuff3": "#CDAF95",
    "peachpuff4": "#8B7765",
    "peru": "#CD853F",
    "pink": "#FFC0CB",
    "pink1": "#FFB5C5",
    "pink2": "#EEA9B8",
    "pink3": "#CD919E",
    "pink4": "#8B636C",
    "plum": "#DDA0DD",
    "plum1": "#FFBBFF",
    "plum2": "#EEAEEE",
    "plum3": "#CD96CD",
    "plum4": "#8B668B",
    "powderblue": "#B0E0E6",
    "purple": "#A020F0",
    "purple1": "#9B30FF",
    "purple2": "#912CEE",
    "purple3": "#7D26CD",
    "purple4": "#551A8B",
    "red": "#FF0000",
    "red1": "#FF0000",
    "red2": "#EE0000",
    "red3": "#CD0000",
    "red4": "#8B0000",
    "rosybrown": "#BC8F8F",
    "rosybrown1": "#FFC1C1",
    "rosybrown2": "#EEB4B4",
    "rosybrown3": "#CD9B9B",
    "rosybrown4": "#8B6969",
    "royalblue": "#4169E1",
    "royalblue1": "#4876FF",
    "royalblue2": "#436EEE",
    "royalblue3": "#3A5FCD",
    "royalblue4": "#27408B",
    "saddlebrown": "#8B4513",
    "salmon": "#FA8072",
    "salmon1": "#FF8C69",
    "salmon2": "#EE8262",
    "salmon3": "#CD7054",
    "salmon4": "#8B4C39",
    "sandybrown": "#F4A460",
    "seagreen": "#2E8B57",
    "seagreen1": "#54FF9F",
    "seagreen2": "#4EEE94",
    "seagreen3": "#43CD80",
    "seagreen4": "#2E8B57",
    "seashell": "#FFF5EE",
    "seashell1": "#FFF5EE",
    "seashell2": "#EEE5DE",
    "seashell3": "#CDC5BF",
    "seashell4": "#8B8682",
    "sienna": "#A0522D",
    "sienna1": "#FF8247",
    "sienna2": "#EE7942",
    "sienna3": "#CD6839",
    "sienna4": "#8B4726",
    "skyblue": "#87CEEB",
    "skyblue1": "#87CEFF",
    "skyblue2": "#7EC0EE",
    "skyblue3": "#6CA6CD",
    "skyblue4": "#4A708B",
    "slateblue": "#6A5ACD",
    "slateblue1": "#836FFF",
    "slateblue2": "#7A67EE",
    "slateblue3": "#6959CD",
    "slateblue4": "#473C8B",
    "slategray": "#708090",
    "slategray1": "#C6E2FF",
    "slategray2": "#B9D3EE",
    "slategray3": "#9FB6CD",
    "slategray4": "#6C7B8B",
    "slategrey": "#708090",
    "snow": "#FFFAFA",
    "snow1": "#FFFAFA",
    "snow2": "#EEE9E9",
    "snow3": "#CDC9C9",
    "snow4": "#8B8989",
    "springgreen": "#00FF7F",
    "springgreen1": "#00FF7F",
    "springgreen2": "#00EE76",
    "springgreen3": "#00CD66",
    "springgreen4": "#008B45",
    "steelblue": "#4682B4",
    "steelblue1": "#63B8FF",
    "steelblue2": "#5CACEE",
    "steelblue3": "#4F94CD",
    "steelblue4": "#36648B",
    "tan": "#D2B48C",
    "tan1": "#FFA54F",
    "tan2": "#EE9A49",
    "tan3": "#CD853F",
    "tan4": "#8B5A2B",
    "thistle": "#D8BFD8",
    "thistle1": "#FFE1FF",
    "thistle2": "#EED2EE",
    "thistle3": "#CDB5CD",
    "thistle4": "#8B7B8B",
    "tomato": "#FF6347",
    "tomato1": "#FF6347",
    "tomato2": "#EE5C42",
    "tomato3": "#CD4F39",
    "tomato4": "#8B3626",
    "turquoise": "#40E0D0",
    "turquoise1": "#00F5FF",
    "turquoise2": "#00E5EE",
    "turquoise3": "#00C5CD",
    "turquoise4": "#00868B",
    "violet": "#EE82EE",
    "violetred": "#D02090",
    "violetred1": "#FF3E96",
    "violetred2": "#EE3A8C",
    "violetred3": "#CD3278",
    "violetred4": "#8B2252",
    "wheat": "#F5DEB3",
    "wheat1": "#FFE7BA",
    "wheat2": "#EED8AE",
    "wheat3": "#CDBA96",
    "wheat4": "#8B7E66",
    "white": "#FFFFFF",
    "whitesmoke": "#F5F5F5",
    "yellow": "#FFFF00",
    "yellow1": "#FFFF00",
    "yellow2": "#EEEE00",
    "yellow3": "#CDCD00",
    "yellow4": "#8B8B00",
    "yellowgreen": "#9ACD32"
}

#@-node:bob.20080115070511.2:<< define leo_color_database >>
#@nl

#@+others
#@+node:bob.20080115070511.3:color database functions
#@+node:bob.20071231111744.2:get / getColor
def getColor(name, default=None):
    """ Translate a named color into #rrggbb' format.

    if 'name' is not a string it is returned unchanged.

    If 'name' is already in '#rrggbb' format then it is returned unchanged.

    If 'name' is not in global_color_database then getColor(default, None)
    is called and that result returned.


    """

    if not g.isString(name):
        return name

    #g.trace(name, default)

    if name[0] == '#':
        return name

    name = name.replace(' ', '').lower()

    if name in leo_color_database:
        return leo_color_database[name]

    if default:
        return getColor(default, default=None)

    return None

get = getColor
#@-node:bob.20071231111744.2:get / getColor
#@+node:bob.20080115070511.4:getRGB / getColorRGB
def getColorRGB(name, default=None):
    """Convert a named color into an (r, g, b) tuple."""

    s = getColor(name, default)

    try:
        color = int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16)
    except:
        color = None

    return color

getRGB = getColorRGB

#@-node:bob.20080115070511.4:getRGB / getColorRGB
#@+node:bob.20080115072302:getCairo / getColorCairo
def getColorCairo(name, default=None):

    """Convert a named color into a cairo color tuple."""

    color = getColorRGB(name, default)
    if color is None:
        return

    r, g, b = color

    return r/255.0, g/255.0, b/255.0

getCairo = getColorCairo

#@-node:bob.20080115072302:getCairo / getColorCairo
#@-node:bob.20080115070511.3:color database functions
#@+node:ekr.20031218072017.2796:class colorizer
class colorizer:
    """Leo's syntax colorer class"""
    def interrupt(self): pass
    #@    @+others
    #@+node:ekr.20031218072017.1605:color.__init__ & helper
    def __init__(self,c):

        self.c = c
        self.frame = c.frame
        self.trace = c.config.getBool('trace_colorizer')
        self.count = 0 # how many times this has been called.
        self.use_hyperlinks = False # True: use hyperlinks and underline "live" links.
        self.enabled = True # True: syntax coloring enabled
        self.fonts = {}
        self.showInvisibles = False # True: show "invisible" characters.
        self.comment_string = None # Set by scanColorDirectives on @comment
        # For incremental coloring.
        self.tags = (
            "blank","comment","cwebName","docPart","keyword","leoKeyword",
            "latexModeBackground","latexModeKeyword",
            "latexBackground","latexKeyword",
            "link","name","nameBrackets","pp","string","tab",
            "elide","bold","bolditalic","italic") # new for wiki styling.
        self.incremental = False
        self.sel = None
        self.lines = []
        self.states = []
        self.last_flag = "unknown"
        self.last_language = "unknown"
        #@    << define colorizer keywords >>
        #@+node:ekr.20031218072017.371:<< define colorizer keywords >>
        #@+others
        #@+node:ekr.20031218072017.372:actionscript keywords
        self.actionscript_keywords = [
        #Jason 2003-07-03 
        #Actionscript keywords for Leo adapted from UltraEdit syntax highlighting
        "break", "call", "continue", "delete", "do", "else", "false", "for", "function", "goto", "if", "in", "new", "null", "return", "true", "typeof", "undefined", "var", "void", "while", "with", "#include", "catch", "constructor", "prototype", "this", "try", "_parent", "_root", "__proto__", "ASnative", "abs", "acos", "appendChild", "asfunction", "asin", "atan", "atan2", "attachMovie", "attachSound", "attributes", "BACKSPACE", "CAPSLOCK", "CONTROL", "ceil", "charAt", "charCodeAt", "childNodes", "chr", "cloneNode", "close", "concat", "connect", "cos", "createElement", "createTextNode", "DELETEKEY", "DOWN", "docTypeDecl", "duplicateMovieClip", "END", "ENTER", "ESCAPE", "enterFrame", "entry", "equal", "eval", "evaluate", "exp", "firstChild", "floor", "fromCharCode", "fscommand", "getAscii", "getBeginIndex", "getBounds", "getBytesLoaded", "getBytesTotal", "getCaretIndex", "getCode", "getDate", "getDay", "getEndIndex", "getFocus", "getFullYear", "getHours", "getMilliseconds", "getMinutes", "getMonth", "getPan", "getProperty", "getRGB", "getSeconds", "getTime", "getTimer", "getTimezoneOffset", "getTransform", "getURL", "getUTCDate", "getUTCDay", "getUTCFullYear", "getUTCHours", "getUTCMilliseconds", "getUTCMinutes", "getUTCMonth", "getUTCSeconds", "getVersion", "getVolume", "getYear", "globalToLocal", "gotoAndPlay", "gotoAndStop", "HOME", "haschildNodes", "hide", "hitTest", "INSERT", "Infinity", "ifFrameLoaded", "ignoreWhite", "indexOf", "insertBefore", "int", "isDown", "isFinite", "isNaN", "isToggled", "join", "keycode", "keyDown", "keyUp", "LEFT", "LN10", "LN2", "LOG10E", "LOG2E", "lastChild", "lastIndexOf", "length", "load", "loaded", "loadMovie", "loadMovieNum", "loadVariables", "loadVariablesNum", "localToGlobal", "log", "MAX_VALUE", "MIN_VALUE", "max", "maxscroll", "mbchr", "mblength", "mbord", "mbsubstring", "min", "NEGATIVE_INFINITY", "NaN", "newline", "nextFrame", "nextScene", "nextSibling", "nodeName", "nodeType", "nodeValue", "on", "onClipEvent", "onClose", "onConnect", "onData", "onLoad", "onXML", "ord", "PGDN", "PGUP", "PI", "POSITIVE_INFINITY", "parentNode", "parseFloat", "parseInt", "parseXML", "play", "pop", "pow", "press", "prevFrame", "previousSibling", "prevScene", "print", "printAsBitmap", "printAsBitmapNum", "printNum", "push", "RIGHT", "random", "release", "removeMovieClip", "removeNode", "reverse", "round", "SPACE", "SQRT1_2", "SQRT2", "scroll", "send", "sendAndLoad", "set", "setDate", "setFocus", "setFullYear", "setHours", "setMilliseconds", "setMinutes", "setMonth", "setPan", "setProperty", "setRGB", "setSeconds", "setSelection", "setTime", "setTransform", "setUTCDate", "setUTCFullYear", "setUTCHours", "setUTCMilliseconds", "setUTCMinutes", "setUTCMonth", "setUTCSeconds", "setVolume", "setYear", "shift", "show", "sin", "slice", "sort", "start", "startDrag", "status", "stop", "stopAllSounds", "stopDrag", "substr", "substring", "swapDepths", "splice", "split", "sqrt", "TAB", "tan", "targetPath", "tellTarget", "toggleHighQuality", "toLowerCase", "toString", "toUpperCase", "trace", "UP", "UTC", "unescape", "unloadMovie", "unLoadMovieNum", "unshift", "updateAfterEvent", "valueOf", "xmlDecl", "_alpha", "_currentframe", "_droptarget", "_focusrect", "_framesloaded", "_height", "_highquality", "_name", "_quality", "_rotation", "_soundbuftime", "_target", "_totalframes", "_url", "_visible", "_width", "_x", "_xmouse", "_xscale", "_y", "_ymouse", "_yscale", "and", "add", "eq", "ge", "gt", "le", "lt", "ne", "not", "or", "Array", "Boolean", "Color", "Date", "Key", "Math", "MovieClip", "Mouse", "Number", "Object", "Selection", "Sound", "String", "XML", "XMLSocket"
        ]
        #@-node:ekr.20031218072017.372:actionscript keywords
        #@+node:bwmulder.20041023131509:ada keywords
        self.ada_keywords = [
            "abort",       "else",       "new",        "return",
            "abs",         "elsif",      "not",        "reverse",
            "abstract",    "end",        "null",
            "accept",      "entry",      "select",
            "access",      "exception",  "separate",
            "aliased",     "exit",       "of",         "subtype",
            "all",                       "or",
            "and",         "for",        "others",     "tagged",
            "array",       "function",   "out",        "task",
            "at",                                      "terminate",
                           "generic",    "package",    "then",
            "begin",       "goto",       "pragma",     "type",
            "body",                      "private",
                           "if",         "procedure",
            "case",        "in",         "protected",  "until",
            "constant",    "is",                       "use",
                                         "raise",
            "declare",                   "range",      "when",
            "delay",       "limited",    "record",     "while",
            "delta",       "loop",       "rem",        "with",
            "digits",                    "renames",
            "do",          "mod",        "requeue",    "xor"
           ]
        #@-node:bwmulder.20041023131509:ada keywords
        #@+node:ekr.20040206072057:c# keywords
        self.csharp_keywords = [
            "abstract","as",
            "base","bool","break","byte",
            "case","catch","char","checked","class","const","continue",
            "decimal","default","delegate","do","double",
            "else","enum","event","explicit","extern",
            "false","finally","fixed","float","for","foreach",
            "get","goto",
            "if","implicit","in","int","interface","internal","is",
            "lock","long",
            "namespace","new","null",
            "object","operator","out","override",
            "params","partial","private","protected","public",
            "readonly","ref","return",
            "sbyte","sealed","set","short","sizeof","stackalloc",
            "static","string","struct","switch",
            "this","throw","true","try","typeof",
            "uint","ulong","unchecked","unsafe","ushort","using",
            "value","virtual","void","volatile",
            "where","while",
            "yield"]
        #@-node:ekr.20040206072057:c# keywords
        #@+node:ekr.20031218072017.373:c/c++/cweb keywords
        self.c_keywords = [
            # C keywords
            "auto","break","case","char","continue",
            "default","do","double","else","enum","extern",
            "float","for","goto","if","int","long","register","return",
            "short","signed","sizeof","static","struct","switch",
            "typedef","union","unsigned","void","volatile","while",
            # C++ keywords
            "asm","bool","catch","class","const","const_cast",
            "delete","dynamic_cast","explicit","false","friend",
            "inline","mutable","namespace","new","operator",
            "private","protected","public","reinterpret_cast","static_cast",
            "template","this","throw","true","try",
            "typeid","typename","using","virtual","wchar_t",
        ]

        self.cweb_keywords = self.c_keywords
        #@-node:ekr.20031218072017.373:c/c++/cweb keywords
        #@+node:ekr.20040401103539:css keywords
        self.css_keywords = [
        #html tags
        "address", "applet", "area", "a", "base", "basefont",
        "big", "blockquote", "body", "br", "b", "caption", "center",
        "cite", "code", "dd", "dfn", "dir", "div", "dl", "dt", "em", "font",
        "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "hr", "html", "img",
        "input", "isindex", "i", "kbd", "link", "li", "link", "map", "menu",
        "meta", "ol", "option", "param", "pre", "p", "samp",
        "select", "small", "span", "strike", "strong", "style", "sub", "sup",
        "table", "td", "textarea", "th", "title", "tr", "tt", "ul", "u", "var",
        #units
        "mm", "cm", "in", "pt", "pc", "em", "ex", "px",
        #colors
        "aqua", "black", "blue", "fuchsia", "gray", "green", "lime", "maroon", "navy", "olive", "purple", "red", "silver", "teal", "yellow", "white",
        #important directive
        "!important",
        #font rules
        "font", "font-family", "font-style", "font-variant", "font-weight", "font-size",
        #font values
        "cursive", "fantasy", "monospace", "normal", "italic", "oblique", "small-caps",
        "bold", "bolder", "lighter", "medium", "larger", "smaller",
        "serif", "sans-serif",
        #background rules
        "background", "background-color", "background-image", "background-repeat", "background-attachment", "background-position",
        #background values
        "contained", "none", "top", "center", "bottom", "left", "right", "scroll", "fixed",
        "repeat", "repeat-x", "repeat-y", "no-repeat",
        #text rules
        "word-spacing", "letter-spacing", "text-decoration", "vertical-align", "text-transform", "text-align", "text-indent", "text-transform", "text-shadow", "unicode-bidi", "line-height",
        #text values
        "normal", "none", "underline", "overline", "blink", "sub", "super", "middle", "top", "text-top", "text-bottom",
        "capitalize", "uppercase", "lowercase", "none", "left", "right", "center", "justify",
        "line-through",
        #box rules
        "margin", "margin-top", "margin-bottom", "margin-left", "margin-right",
        "margin", "padding-top", "padding-bottom", "padding-left", "padding-right",
        "border", "border-width", "border-style", "border-top", "border-top-width", "border-top-style", "border-bottom", "border-bottom-width", "border-bottom-style", "border-left", "border-left-width", "border-left-style", "border-right", "border-right-width", "border-right-style", "border-color",
        #box values
        "width", "height", "float", "clear",
        "auto", "thin", "medium", "thick", "left", "right", "none", "both",
        "none", "dotted", "dashed", "solid", "double", "groove", "ridge", "inset", "outset",
        #display rules
        "display", "white-space", 
        "min-width", "max-width", "min-height", "max-height",
        "outline-color", "outline-style", "outline-width",
        #display values
        "run-in", "inline-block", "list-item", "block", "inline", "none", "normal", "pre", "nowrap", "table-cell", "table-row", "table-row-group", "table-header-group", "inline-table", "table-column", "table-column-group", "table-cell", "table-caption"
        #list rules
        "list-style", "list-style-type", "list-style-image", "list-style-position",
        #list values
        "disc", "circle", "square", "decimal", "decimal-leading-zero", "none",
        "lower-roman", "upper-roman", "lower-alpha", "upper-alpha", "lower-latin", "upper-latin",
        #table rules
        "border-collapse", "caption-side",
        #table-values
        "empty-cells", "table-layout",
        #misc values/rules
        "counter-increment", "counter-reset",
        "marker-offset", "z-index",
        "cursor", "direction", "marks", "quotes",
        "clip", "content", "orphans", "overflow", "visibility",
        #aural rules
        "pitch", "range", "pitch-during", "cue-after", "pause-after", "cue-before", "pause-before", "speak-header", "speak-numeral", "speak-punctuation", "speed-rate", "play-during", "voice-family",
        #aural values
        "stress", "azimuth", "elevation", "pitch", "richness", "volume",
        "page-break", "page-after", "page-inside"]
        #@-node:ekr.20040401103539:css keywords
        #@+node:ekr.20031218072017.374:elisp keywords
        # EKR: needs more work.
        self.elisp_keywords = [
            # Maybe...
            "error","princ",
            # More typical of other lisps...
            "apply","eval",
            "t","nil",
            "and","or","not",
            "cons","car","cdr",
            "cond",
            "defconst","defun","defvar",
            "eq","ne","equal","gt","ge","lt","le",
            "if",
            "let",
            "mapcar",
            "prog","progn",
            "set","setq",
            "type-of",
            "unless",
            "when","while"]
        #@-node:ekr.20031218072017.374:elisp keywords
        #@+node:ekr.20031218072017.375:html keywords
        # No longer used by syntax colorer.
        self.html_keywords = []

        if 0: # Not used at present.
            self.unused_keywords = [
                # html constructs.
                "a","body","cf",
                "h1","h2","h3","h4","h5","h6",
                "head","html","hr",
                "i","img","li","lu","meta",
                "p","title","ul",
                # Common tags
                "caption","col","colgroup",
                "table","tbody","td","tfoot","th","thead","tr",
                "script","style"]

            self.html_specials = [ "<%","%>" ]
        #@-node:ekr.20031218072017.375:html keywords
        #@+node:ekr.20031218072017.376:java keywords
        self.java_keywords = [
            "abstract","boolean","break","byte","byvalue",
            "case","cast","catch","char","class","const","continue",
            "default","do","double","else","extends",
            "false","final","finally","float","for","future",
            "generic","goto","if","implements","import","inner",
            "instanceof","int","interface","long","native",
            "new","null","operator","outer",
            "package","private","protected","public","rest","return",
            "short","static","super","switch","synchronized",
            "this","throw","transient","true","try",
            "var","void","volatile","while"]
        #@-node:ekr.20031218072017.376:java keywords
        #@+node:ekr.20031218072017.377:latex keywords
        #If you see two idenitical words, with minor capitalization differences
        #DO NOT ASSUME that they are the same word. For example \vert produces
        #a single vertical line and \Vert produces a double vertical line
        #Marcus A. Martin.

        self.latex_special_keyword_characters = "@(){}%"

        self.latex_keywords = [
            #special keyworlds
            "\\%", # 11/9/03
            "\\@", "\\(", "\\)", "\\{", "\\}",
            #A
            "\\acute", "\\addcontentsline", "\\addtocontents", "\\addtocounter", "\\address",
            "\\addtolength", "\\addvspace", "\\AE", "\\ae", "\\aleph", "\\alph", "\\angle",
            "\\appendix", 
            "\\approx", "\\arabic", "\\arccos", "\\arcsin", "\\arctan", "\\ast", "\\author",
            #B
            "\\b", "\\backmatter", "\\backslash", "\\bar", "\\baselineskip", "\\baselinestretch",
            "\\begin", "\\beta", "\\bezier", "\\bf", "\\bfseries", "\\bibitem", "\\bigcap",
            "\\bigcup", "\\bigodot", "\\bigoplus", "\\bigotimes", "\\bigskip", "\\biguplus",
            "\\bigvee", "\\bigwedge", "\\bmod", "\\boldmath", "\\Box", "\\breve", "\\bullet",
            #C
            "\\c", "\\cal", "\\caption", "\\cdot", "\\cdots", "\\centering", "\\chapter",
            "\\check", "\\chi", "\\circ", "\\circle", "\\cite", "\\cleardoublepage", "\\clearpage",
            "\\cline", "\\closing", "\\clubsuit", "\\coprod", "\\copywright", "\\cos", "\\cosh",
            "\\cot", "\\coth", "csc",
            #D
            "\\d", "\\dag", "\\dashbox", "\\date", "\\ddag", "\\ddot", "\\ddots", "\\decl",
            "\\deg", "\\Delta", 
            "\\delta", "\\depthits", "\\det", 
            "\\DH", "\\dh", "\\Diamond", "\\diamondsuit", "\\dim", "\\div", "\\DJ", "\\dj",
            "\\documentclass", "\\documentstyle", 
            "\\dot", "\\dotfil", "\\downarrow",
            #E
            "\\ell", "\\em", "\\emph", "\\end", "\\enlargethispage", "\\ensuremath",
            "\\enumi", "\\enuii", "\\enumiii", "\\enuiv", "\\epsilon", "\\equation", "\\equiv",
            "\\eta", "\\example", "\\exists", "\\exp",
            #F
            "\\fbox", "\\figure", "\\flat", "\\flushbottom", "\\fnsymbol", "\\footnote",
            "\\footnotemark", "\\fotenotesize", 
            "\\footnotetext", "\\forall", "\\frac", "\\frame", "\\framebox", "\\frenchspacing",
            "\\frontmatter",
            #G
            "\\Gamma", "\\gamma", "\\gcd", "\\geq", "\\gg", "\\grave", "\\guillemotleft", 
            "\\guillemotright", "\\guilsinglleft", "\\guilsinglright",
            #H
            "\\H", "\\hat", "\\hbar", "\\heartsuit", "\\heightits", "\\hfill", "\\hline", "\\hom",
            "\\hrulefill", "\\hspace", "\\huge", "\\Huge", "\\hyphenation"
            #I
            "\\Im", "\\imath", "\\include", "includeonly", "indent", "\\index", "\\inf", "\\infty", 
            "\\input", "\\int", "\\iota", "\\it", "\\item", "\\itshape",
            #J
            "\\jmath", "\\Join",
            #K
            "\\k", "\\kappa", "\\ker", "\\kill",
            #L
            "\\label", "\\Lambda", "\\lambda", "\\langle", "\\large", "\\Large", "\\LARGE", 
            "\\LaTeX", "\\LaTeXe", 
            "\\ldots", "\\leadsto", "\\left", "\\Leftarrow", "\\leftarrow", "\\lefteqn", "\\leq",
            "\\lg", "\\lhd", "\\lim", "\\liminf", "\\limsup", "\\line", "\\linebreak", 
            "\\linethickness", "\\linewidth", "\\listfiles",
            "\\ll", "\\ln", "\\location", "\\log", "\\Longleftarrow", "\\longleftarrow", 
            "\\Longrightarrow", "longrightarrow",
            #M
            "\\mainmatter", "\\makebox", "\\makeglossary", "\\makeindex","\\maketitle", "\\markboth", "\\markright",
            "\\mathbf", "\\mathcal", "\\mathit", "\\mathnormal", "\\mathop",
            "\\mathrm", "\\mathsf", "\\mathtt", "\\max", "\\mbox", "\\mdseries", "\\medskip",
            "\\mho", "\\min", "\\mp", "\\mpfootnote", "\\mu", "\\multicolumn", "\\multiput",
            #N
            "\\nabla", "\\natural", "\\nearrow", "\\neq", "\\newcommand", "\\newcounter", 
            "\\newenvironment", "\\newfont",
            "\\newlength", "\\newline", "\\newpage", "\\newsavebox", "\\newtheorem", "\\NG", "\\ng",
            "\\nocite", "\\noindent", "\\nolinbreak", "\\nopagebreak", "\\normalsize",
            "\\not", "\\nu", "nwarrow",
            #O
            "\\Omega", "\\omega", "\\onecolumn", "\\oint", "\\opening", "\\oval", 
            "\\overbrace", "\\overline",
            #P
            "\\P", "\\page", "\\pagebreak", "\\pagenumbering", "\\pageref", "\\pagestyle", 
            "\\par", "\\parbox", "\\paragraph", "\\parindent", "\\parskip", "\\part", 
            "\\partial", "\\per", "\\Phi", "\\phi", "\\Pi", "\\pi", "\\pm", 
            "\\pmod", "\\pounds", "\\prime", "\\printindex", "\\prod", "\\propto", "\\protext", 
            "\\providecomamnd", "\\Psi", "\\psi", "\\put",
            #Q
            "\\qbezier", "\\quoteblbase", "\\quotesinglbase",
            #R
            "\\r", "\\raggedbottom", "\\raggedleft", "\\raggedright", "\\raisebox", "\\rangle", 
            "\\Re", "\\ref", "\\renewcommand", "\\renewenvironment", "\\rhd", "\\rho", "\\right", 
            "\\Rightarrow", "\\rightarrow", "\\rm", "\\rmfamily",
            "\\Roman", "\\roman", "\\rule", 
            #S
            "\\s", "\\samepage", "\\savebox", "\\sbox", "\\sc", "\\scriptsize", "\\scshape", 
            "\\searrow", "\\sec", "\\section",
            "\\setcounter", "\\setlength", "\\settowidth", "\\settodepth", "\\settoheight", 
            "\\settowidth", "\\sf", "\\sffamily", "\\sharp", "\\shortstack", "\\Sigma", "\\sigma", 
            "\\signature", "\\sim", "\\simeq", "\\sin", "\\sinh", "\\sl", "\\SLiTeX",
            "\\slshape", "\\small", "\\smallskip", "\\spadesuit", "\\sqrt", "\\sqsubset",
            "\\sqsupset", "\\SS",
            "\\stackrel", "\\star", "\\subsection", "\\subset", 
            "\\subsubsection", "\\sum", "\\sup", "\\supressfloats", "\\surd", "\\swarrow",
            #T
            "\\t", "\\table", "\\tableofcontents", "\\tabularnewline", "\\tan", "\\tanh", 
            "\\tau", "\\telephone", "\\TeX", "\\textbf",
            "\\textbullet", "\\textcircled", "\\textcompworkmark", "\\textemdash", 
            "\\textendash", "\\textexclamdown", "\\textheight", "\\textquestiondown", 
            "\\textquoteblleft", "\\textquoteblright", "\\textquoteleft",
            "\\textperiod", "\\textquotebl", "\\textquoteright", "\\textmd", "\\textit", "\\textrm", 
            "\\textsc", "\\textsl", "\\textsf", "\\textsuperscript", "\\texttt", "\\textup",
            "\\textvisiblespace", "\\textwidth", "\\TH", "\\th", "\\thanks", "\\thebibligraphy",
            "\\Theta", "theta", 
            "\\tilde", "\\thinlines", 
            "\\thispagestyle", "\\times", "\\tiny", "\\title", "\\today", "\\totalheightits", 
            "\\triangle", "\\tt", 
            "\\ttfamily", "\\twocoloumn", "\\typeout", "\\typein",
            #U
            "\\u", "\\underbrace", "\\underline", "\\unitlength", "\\unlhd", "\\unrhd", "\\Uparrow",
            "\\uparrow", "\\updownarrow", "\\upshape", "\\Upsilon", "\\upsilon", "\\usebox",
            "\\usecounter", "\\usepackage", 
            #V
            "\\v", "\\value", "\\varepsilon", "\\varphi", "\\varpi", "\\varrho", "\\varsigma", 
            "\\vartheta", "\\vdots", "\\vec", "\\vector", "\\verb", "\\Vert", "\\vert", "\\vfill",
            "\\vline", "\\vphantom", "\\vspace",
            #W
            "\\widehat", "\\widetilde", "\\widthits", "\\wp",
            #X
            "\\Xi", "\\xi",
            #Z
            "\\zeta" ]
        #@-node:ekr.20031218072017.377:latex keywords
        #@+node:ekr.20060328110802:lua keywords
        # ddm 13/02/06
        self.lua_keywords = [
            "and", "break", "do", "else", "elseif", "end",
            "false", "for", "function", "if", "in", "local",
            "nil", "not", "or", "repeat", "return", "then",
            "true", "until", "while",
        ]
        #@-node:ekr.20060328110802:lua keywords
        #@+node:ekr.20031218072017.378:pascal keywords
        self.pascal_keywords = [
            "and","array","as","begin",
            "case","const","class","constructor","cdecl"
            "div","do","downto","destructor","dispid","dynamic",
            "else","end","except","external",
            "false","file","for","forward","function","finally",
            "goto","if","in","is","label","library",
            "mod","message","nil","not","nodefault""of","or","on",
            "procedure","program","packed","pascal",
            "private","protected","public","published",
            "record","repeat","raise","read","register",
            "set","string","shl","shr","stdcall",
            "then","to","true","type","try","until","unit","uses",
            "var","virtual","while","with","xor"
            # object pascal
            "asm","absolute","abstract","assembler","at","automated",
            "finalization",
            "implementation","inherited","initialization","inline","interface",
            "object","override","resident","resourcestring",
            "threadvar",
            # limited contexts
            "exports","property","default","write","stored","index","name" ]
        #@-node:ekr.20031218072017.378:pascal keywords
        #@+node:ekr.20031218072017.379:perl/perlpod keywords
        self.perl_keywords = [
            "continue","do","else","elsif","format","for","format","for","foreach",
            "if","local","package","sub","tr","unless","until","while","y",
            # Comparison operators
            "cmp","eq","ge","gt","le","lt","ne",
            # Matching ooperators
            "m","s",
            # Unary functions
            "alarm","caller","chdir","cos","chroot","exit","eval","exp",
            "getpgrp","getprotobyname","gethostbyname","getnetbyname","gmtime",
            "hex","int","length","localtime","log","ord","oct",
            "require","reset","rand","rmdir","readlink",
            "scalar","sin","sleep","sqrt","srand","umask",
            # Transfer ops
            "next","last","redo","go","dump",
            # File operations...
            "select","open",
            # FL ops
            "binmode","close","closedir","eof",
            "fileno","getc","getpeername","getsockname","lstat",
            "readdir","rewinddir","stat","tell","telldir","write",
            # FL2 ops
            "bind","connect","flock","listen","opendir",
            "seekdir","shutdown","truncate",
            # FL32 ops
            "accept","pipe",
            # FL3 ops
            "fcntl","getsockopt","ioctl","read",
            "seek","send","sysread","syswrite",
            # FL4 & FL5 ops
            "recv","setsocket","socket","socketpair",
            # Array operations
            "pop","shift","split","delete",
            # FLIST ops
            "sprintf","grep","join","pack",
            # LVAL ops
            "chop","defined","study","undef",
            # f0 ops
            "endhostent","endnetent","endservent","endprotoent",
            "endpwent","endgrent","fork",
            "getgrent","gethostent","getlogin","getnetent","getppid",
            "getprotoent","getpwent","getservent",
            "setgrent","setpwent","time","times","wait","wantarray",
            # f1 ops
            "getgrgid","getgrnam","getprotobynumber","getpwnam","getpwuid",
            "sethostent","setnetent","setprotoent","setservent",
            # f2 ops
            "atan2","crypt",
            "gethostbyaddr","getnetbyaddr","getpriority","getservbyname","getservbyport",
            "index","link","mkdir","msgget","rename",
            "semop","setpgrp","symlink","unpack","waitpid",
            # f2 or 3 ops
            "index","rindex","substr",
            # f3 ops
            "msgctl","msgsnd","semget","setpriority","shmctl","shmget","vec",
            # f4 & f5 ops
            "semctl","shmread","shmwrite","msgrcv",
            # Assoc ops
            "dbmclose","each","keys","values",
            # List ops
            "chmod","chown","die","exec","kill",
            "print","printf","return","reverse",
            "sort","system","syscall","unlink","utime","warn",
        ]

        self.perlpod_keywords = self.perl_keywords
        #@-node:ekr.20031218072017.379:perl/perlpod keywords
        #@+node:ekr.20031218072017.380:php keywords
        self.php_keywords = [ # 08-SEP-2002 DTHEIN
            "__CLASS__", "__FILE__", "__FUNCTION__", "__LINE__",
            "and", "as", "break",
            "case", "cfunction", "class", "const", "continue",
            "declare", "default", "do",
            "else", "elseif", "enddeclare", "endfor", "endforeach",
            "endif", "endswitch",  "endwhile", "eval", "extends",
            "for", "foreach", "function", "global", "if",
            "new", "old_function", "or", "static", "switch",
            "use", "var", "while", "xor" ]

        # The following are supposed to be followed by ()
        self.php_paren_keywords = [
            "array", "die", "echo", "empty", "exit",
            "include", "include_once", "isset", "list",
            "print", "require", "require_once", "return",
            "unset" ]

        # The following are handled by special case code:
        # "<?php", "?>"
        #@-node:ekr.20031218072017.380:php keywords
        #@+node:ekr.20050618052653:plsql keywords
        self.plsql_keywords = [
        # reserved keywords
        "abort",
        "accept",
        "access",
        "add",
        "admin",
        "after",
        "all",
        "allocate",
        "alter",
        "analyze",
        "and",
        "any",
        "archive",
        "archivelog",
        "array",
        "arraylen",
        "as",
        "asc",
        "assert",
        "assign",
        "at",
        "audit",
        "authorization",
        "avg",
        "backup",
        "base_table",
        "become",
        "before",
        "begin",
        "between",
        "binary_integer",
        "block",
        "body",
        "boolean",
        "by",
        "cache",
        "cancel",
        "cascade",
        "case",
        "change",
        "char",
        "char_base",
        "character",
        "check",
        "checkpoint",
        "close",
        "cluster",
        "clusters",
        "cobol",
        "colauth",
        "column",
        "columns",
        "comment",
        "commit",
        "compile",
        "compress",
        "connect",
        "constant",
        "constraint",
        "constraints",
        "contents",
        "continue",
        "controlfile",
        "count",
        "crash",
        "create",
        "current",
        "currval",
        "cursor",
        "cycle",
        "data_base",
        "database",
        "datafile",
        "date",
        "dba",
        "debugoff",
        "debugon",
        "dec",
        "decimal",
        "declare",
        "default",
        "definition",
        "delay",
        "delete",
        "delta",
        "desc",
        "digits",
        "disable",
        "dismount",
        "dispose",
        "distinct",
        "distinct",
        "do",
        "double",
        "drop",
        "drop",
        "dump",
        "each",
        "else",
        "else",
        "elsif",
        "enable",
        "end",
        "end",
        "entry",
        "escape",
        "events",
        "except",
        "exception",
        "exception_init",
        "exceptions",
        "exclusive",
        "exec",
        "execute",
        "exists",
        "exists",
        "exit",
        "explain",
        "extent",
        "externally",
        "false",
        "fetch",
        "fetch",
        "file",
        "float",
        "float",
        "flush",
        "for",
        "for",
        "force",
        "foreign",
        "form",
        "fortran",
        "found",
        "freelist",
        "freelists",
        "from",
        "from",
        "function",
        "generic",
        "go",
        "goto",
        "grant",
        "group",
        "groups",
        "having",
        "identified",
        "if",
        "immediate",
        "in",
        "including",
        "increment",
        "index",
        "indexes",
        "indicator",
        "initial",
        "initrans",
        "insert",
        "instance",
        "int",
        "integer",
        "intersect",
        "into",
        "is",
        "key",
        "language",
        "layer",
        "level",
        "like",
        "limited",
        "link",
        "lists",
        "lock",
        "logfile",
        "long",
        "loop",
        "manage",
        "manual",
        "max",
        "maxdatafiles",
        "maxextents",
        "maxinstances",
        "maxlogfiles",
        "maxloghistory",
        "maxlogmembers",
        "maxtrans",
        "maxvalue",
        "min",
        "minextents",
        "minus",
        "minvalue",
        "mlslabel",
        "mod",
        "mode",
        "modify",
        "module",
        "mount",
        "natural",
        "new",
        "new",
        "next",
        "nextval",
        "noarchivelog",
        "noaudit",
        "nocache",
        "nocompress",
        "nocycle",
        "nomaxvalue",
        "nominvalue",
        "none",
        "noorder",
        "noresetlogs",
        "normal",
        "nosort",
        "not",
        "notfound",
        "nowait",
        "null",
        "number",
        "number_base",
        "numeric",
        "of",
        "off",
        "offline",
        "old",
        "on",
        "online",
        "only",
        "open",
        "open",
        "optimal",
        "option",
        "or",
        "order",
        "others",
        "out",
        "own",
        "package",
        "package",
        "parallel",
        "partition",
        "pctfree",
        "pctincrease",
        "pctused",
        "plan",
        "pli",
        "positive",
        "pragma",
        "precision",
        "primary",
        "prior",
        "private",
        "private",
        "privileges",
        "procedure",
        "procedure",
        "profile",
        "public",
        "quota",
        "raise",
        "range",
        "raw",
        "read",
        "real",
        "record",
        "recover",
        "references",
        "referencing",
        "release",
        "remr",
        "rename",
        "resetlogs",
        "resource",
        "restricted",
        "return",
        "reuse",
        "reverse",
        "revoke",
        "role",
        "roles",
        "rollback",
        "row",
        "rowid",
        "rowlabel",
        "rownum",
        "rows",
        "rowtype",
        "run",
        "savepoint",
        "schema",
        "scn",
        "section",
        "segment",
        "select",
        "select",
        "separate",
        "sequence",
        "session",
        "set",
        "set",
        "share",
        "shared",
        "size",
        "size",
        "smallint",
        "smallint",
        "snapshot",
        "some",
        "sort",
        "space",
        "sql",
        "sqlbuf",
        "sqlcode",
        "sqlerrm",
        "sqlerror",
        "sqlstate",
        "start",
        "start",
        "statement",
        "statement_id",
        "statistics",
        "stddev",
        "stop",
        "storage",
        "subtype",
        "successful",
        "sum",
        "sum",
        "switch",
        "synonym",
        "sysdate",
        "system",
        "tabauth",
        "table",
        "tables",
        "tables",
        "tablespace",
        "task",
        "temporary",
        "terminate",
        "then",
        "thread",
        "time",
        "to",
        "tracing",
        "transaction",
        "trigger",
        "triggers",
        "true",
        "truncate",
        "type",
        "uid",
        "under",
        "union",
        "unique",
        "unlimited",
        "until",
        "update",
        "use",
        "user",
        "using",
        "validate",
        "values",
        "varchar",
        "varchar2",
        "variance",
        "view",
        "views",
        "when",
        "whenever",
        "where",
        "while",
        "with",
        "work",
        "write",
        "xor" ]
        #@-node:ekr.20050618052653:plsql keywords
        #@+node:ekr.20031218072017.381:python keywords
        self.python_keywords = [
            "and",       "del",       "for",       "is",        "raise",    
            "assert",    "elif",      "from",      "lambda",    "return",   
            "break",     "else",      "global",    "not",       "try",      
            "class",     "except",    "if",        "or",        "yield",   
            "continue",  "exec",      "import",    "pass",      "while",
            "def",       "finally",   "in",        "print"]
        #@-node:ekr.20031218072017.381:python keywords
        #@+node:ekr.20040331145826:rapidq keywords
        self.rapidq_keywords = [
        # Syntax file for RapidQ
        "$APPTYPE","$DEFINE","$ELSE","$ENDIF","$ESCAPECHARS","$IFDEF","$IFNDEF",
        "$INCLUDE","$MACRO","$OPTIMIZE","$OPTION","$RESOURCE","$TYPECHECK","$UNDEF",
        "ABS","ACOS","ALIAS","AND","AS","ASC","ASIN","ATAN","ATN","BIN$","BIND","BYTE",
        "CALL","CALLBACK","CALLFUNC","CASE","CEIL","CHDIR","CHDRIVE","CHR$","CINT",
        "CLNG","CLS","CODEPTR","COMMAND$","COMMANDCOUNT","CONSOLE","CONST","CONSTRUCTOR",
        "CONVBASE$","COS","CREATE","CSRLIN","CURDIR$","DATA","DATE$","DEC","DECLARE",
        "DEFBYTE","DEFDBL","DEFDWORD","DEFINT","DEFLNG","DEFSHORT","DEFSNG","DEFSTR",
        "DEFWORD","DELETE$","DIM","DIR$","DIREXISTS","DO","DOEVENTS","DOUBLE","DWORD",
        "ELSE","ELSEIF","END","ENVIRON","ENVIRON$","EVENT","EXIT","EXP","EXTENDS",
        "EXTRACTRESOURCE","FIELD$","FILEEXISTS","FIX","FLOOR","FOR","FORMAT$","FRAC",
        "FUNCTION","FUNCTIONI","GET$","GOSUB","GOTO","HEX$","IF","INC","INITARRAY",
        "INKEY$","INP","INPUT","INPUT$","INPUTHANDLE","INSERT$","INSTR","INT","INTEGER",
        "INV","IS","ISCONSOLE","KILL","KILLMESSAGE","LBOUND","LCASE$","LEFT$","LEN",
        "LFLUSH","LIB","LIBRARYINST","LOCATE","LOG","LONG","LOOP","LPRINT","LTRIM$",
        "MEMCMP","MESSAGEBOX","MESSAGEDLG","MID$","MKDIR","MOD","MOUSEX","MOUSEY",
        "NEXT","NOT","OFF","ON","OR","OUT","OUTPUTHANDLE","PARAMSTR$","PARAMSTRCOUNT",
        "PARAMVAL","PARAMVALCOUNT","PCOPY","PEEK","PLAYWAV","POKE","POS","POSTMESSAGE",
        "PRINT","PROPERTY","QUICKSORT","RANDOMIZE","REDIM","RENAME","REPLACE$",
        "REPLACESUBSTR$","RESOURCE","RESOURCECOUNT","RESTORE","RESULT","RETURN",
        "REVERSE$","RGB","RIGHT$","RINSTR","RMDIR","RND","ROUND","RTRIM$","RUN",
        "SCREEN","SELECT","SENDER","SENDMESSAGE","SETCONSOLETITLE","SGN","SHELL",
        "SHL","SHORT","SHOWMESSAGE","SHR","SIN","SINGLE","SIZEOF","SLEEP","SOUND",
        "SPACE$","SQR","STACK","STATIC","STEP","STR$","STRF$","STRING","STRING$",
        "SUB","SUBI","SWAP","TALLY","TAN","THEN","TIME$","TIMER","TO","TYPE","UBOUND",
        "UCASE$","UNLOADLIBRARY","UNTIL","VAL","VARIANT","VARPTR","VARPTR$","VARTYPE",
        "WEND","WHILE","WITH","WORD","XOR"]
        #@-node:ekr.20040331145826:rapidq keywords
        #@+node:sps.20081213155951.1:ruby keywords
        self.ruby_keywords = [
        # ruby keywords
        # based on "Ruby in a Nutshell"
        "BEGIN",    "do",     "next",   "then",
        "END",      "else",   "nil",    "true",
        "alias",    "elsif",  "not",    "undef",
        "and",      "end",    "or",     "unless",
        "begin",    "ensure", "redo",   "until",
        "break",    "false",  "rescue", "when",
        "case",     "for",    "retry",  "while",
        "class",    "if",     "return", "yield",
        "def",      "in",     "self",   "__FILE__",
        "defined?", "module", "super",  "__LINE__",
        ]
        #@-node:sps.20081213155951.1:ruby keywords
        #@+node:ekr.20031218072017.382:rebol keywords
        self.rebol_keywords = [
        #Jason 2003-07-03 
        #based on UltraEdit syntax highlighting
        "about", "abs", "absolute", "add", "alert", "alias", "all", "alter", "and", "and~", "any", "append", "arccosine", "arcsine", "arctangent", "array", "ask", "at",  
        "back", "bind", "boot-prefs", "break", "browse", "build-port", "build-tag",  
        "call", "caret-to-offset", "catch", "center-face", "change", "change-dir", "charset", "checksum", "choose", "clean-path", "clear", "clear-fields", "close", "comment", "complement", "compose", "compress", "confirm", "continue-post", "context", "copy", "cosine", "create-request", "crypt", "cvs-date", "cvs-version",  
        "debase", "decode-cgi", "decode-url", "decompress", "deflag-face", "dehex", "delete", "demo", "desktop", "detab", "dh-compute-key", "dh-generate-key", "dh-make-key", "difference", "dirize", "disarm", "dispatch", "divide", "do", "do-boot", "do-events", "do-face", "do-face-alt", "does", "dsa-generate-key", "dsa-make-key", "dsa-make-signature", "dsa-verify-signature",  
        "echo", "editor", "either", "else", "emailer", "enbase", "entab", "exclude", "exit", "exp", "extract", 
        "fifth", "find", "find-key-face", "find-window", "flag-face", "first", "flash", "focus", "for", "forall", "foreach", "forever", "form", "forskip", "fourth", "free", "func", "function",  
        "get", "get-modes", "get-net-info", "get-style",  
        "halt", "has", "head", "help", "hide", "hide-popup",  
        "if", "import-email", "in", "inform", "input", "insert", "insert-event-func", "intersect", 
        "join", 
        "last", "launch", "launch-thru", "layout", "license", "list-dir", "load", "load-image", "load-prefs", "load-thru", "log-10", "log-2", "log-e", "loop", "lowercase",  
        "make", "make-dir", "make-face", "max", "maximum", "maximum-of", "min", "minimum", "minimum-of", "mold", "multiply",  
        "negate", "net-error", "next", "not", "now",  
        "offset-to-caret", "open", "open-events", "or", "or~", 
        "parse", "parse-email-addrs", "parse-header", "parse-header-date", "parse-xml", "path-thru", "pick", "poke", "power", "prin", "print", "probe", "protect", "protect-system",  
        "q", "query", "quit",  
        "random", "read", "read-io", "read-net", "read-thru", "reboot", "recycle", "reduce", "reform", "rejoin", "remainder", "remold", "remove", "remove-event-func", "rename", "repeat", "repend", "replace", "request", "request-color", "request-date", "request-download", "request-file", "request-list", "request-pass", "request-text", "resend", "return", "reverse", "rsa-encrypt", "rsa-generate-key", "rsa-make-key", 
        "save", "save-prefs", "save-user", "scroll-para", "second", "secure", "select", "send", "send-and-check", "set", "set-modes", "set-font", "set-net", "set-para", "set-style", "set-user", "set-user-name", "show", "show-popup", "sine", "size-text", "skip", "sort", "source", "split-path", "square-root", "stylize", "subtract", "switch",  
        "tail", "tangent", "textinfo", "third", "throw", "throw-on-error", "to", "to-binary", "to-bitset", "to-block", "to-char", "to-date", "to-decimal", "to-email", "to-event", "to-file", "to-get-word", "to-hash", "to-hex", "to-idate", "to-image", "to-integer", "to-issue", "to-list", "to-lit-path", "to-lit-word", "to-local-file", "to-logic", "to-money", "to-none", "to-pair", "to-paren", "to-path", "to-rebol-file", "to-refinement", "to-set-path", "to-set-word", "to-string", "to-tag", "to-time", "to-tuple", "to-url", "to-word", "trace", "trim", "try",  
        "unfocus", "union", "unique", "uninstall", "unprotect", "unset", "until", "unview", "update", "upgrade", "uppercase", "usage", "use",  
        "vbug", "view", "view-install", "view-prefs",  
        "wait", "what", "what-dir", "while", "write", "write-io",  
        "xor", "xor~",  
        "action!", "any-block!", "any-function!", "any-string!", "any-type!", "any-word!",  
        "binary!", "bitset!", "block!",  
        "char!",  
        "datatype!", "date!", "decimal!", 
        "email!", "error!", "event!",  
        "file!", "function!",  
        "get-word!",  
        "hash!",  
        "image!", "integer!", "issue!",  
        "library!", "list!", "lit-path!", "lit-word!", "logic!",  
        "money!",  
        "native!", "none!", "number!",  
        "object!", "op!",  
        "pair!", "paren!", "path!", "port!",  
        "refinement!", "routine!",  
        "series!", "set-path!", "set-word!", "string!", "struct!", "symbol!",  
        "tag!", "time!", "tuple!",  
        "unset!", "url!",  
        "word!",  
        "any-block?", "any-function?", "any-string?", "any-type?", "any-word?",  
        "binary?", "bitset?", "block?",  
        "char?", "connected?", "crypt-strength?", 
        "datatype?", "date?", "decimal?", "dir?",  
        "email?", "empty?", "equal?", "error?", "even?", "event?", "exists?", "exists-key?",
        "file?", "flag-face?", "found?", "function?",  
        "get-word?", "greater-or-equal?", "greater?",  
        "hash?", "head?",  
        "image?", "in-window?", "index?", "info?", "input?", "inside?", "integer?", "issue?",  
        "length?", "lesser-or-equal?", "lesser?", "library?", "link-app?", "link?", "list?", "lit-path?", "lit-word?", "logic?",  
        "modified?", "money?",  
        "native?", "negative?", "none?", "not-equal?", "number?",  
        "object?", "odd?", "offset?", "op?", "outside?",  
        "pair?", "paren?", "path?", "port?", "positive?",  
        "refinement?", "routine?",  
        "same?", "screen-offset?", "script?", "series?", "set-path?", "set-word?", "size?", "span?", "strict-equal?", "strict-not-equal?", "string?", "struct?",  
        "tag?", "tail?", "time?", "tuple?", "type?",  
        "unset?", "url?",  
        "value?", "view?", 
        "within?", "word?",  
        "zero?"
        ]
        #@-node:ekr.20031218072017.382:rebol keywords
        #@+node:ekr.20040401111125:shell keywords
        self.shell_keywords = [
            # reserved keywords
            "case","do","done","elif","else","esac","fi",
            "for","if","in","then",
            "until","while",
            "break","cd","chdir","continue","eval","exec",
            "exit","kill","newgrp","pwd","read","readonly",
            "return","shift","test","trap","ulimit",
            "umask","wait" ]
        #@-node:ekr.20040401111125:shell keywords
        #@+node:ekr.20031218072017.383:tcl/tk keywords
        self.tcltk_keywords = [ # Only the tcl keywords are here.
            "after",     "append",    "array",
            "bgerror",   "binary",    "break",
            "catch",     "cd",        "clock",
            "close",     "concat",    "continue",
            "dde",
            "encoding",  "eof",       "eval",
            "exec",      "exit",      "expr",
            "fblocked",  "fconfigure","fcopy",     "file",      "fileevent",
            "filename",  "flush",     "for",       "foreach",   "format",
            "gets",      "glob",      "global",
            "history",
            "if",        "incr",      "info",      "interp",
            "join",
            "lappend",   "lindex",    "linsert",   "list",      "llength",
            "load",      "lrange",    "lreplace",  "lsearch",   "lsort",
            "memory",    "msgcat",
            "namespace",
            "open",
            "package",   "parray",    "pid",
            "proc",      "puts",      "pwd",
            "read",      "regexp",    "registry",   "regsub",
            "rename",    "resource",  "return",
            "scan",      "seek",      "set",        "socket",   "source",
            "split",     "string",    "subst",      "switch",
            "tell",      "time",      "trace",
            "unknown",   "unset",     "update",     "uplevel",   "upvar",
            "variable",  "vwait",
            "while" ]
        #@-node:ekr.20031218072017.383:tcl/tk keywords
        #@-others
        #@-node:ekr.20031218072017.371:<< define colorizer keywords >>
        #@nl
        #@    << ivars for communication between colorizeAnyLanguage and its allies >>
        #@+node:ekr.20031218072017.1606:<< ivars for communication between colorizeAnyLanguage and its allies >>
        # Copies of arguments.
        self.p = None
        self.language = None
        self.flag = None
        self.killFlag = False
        self.line_index = 0

        # Others.
        self.single_comment_start = None
        self.block_comment_start = None
        self.block_comment_end = None
        self.case_sensitiveLanguage = True
        self.has_string = None
        self.string_delims = ("'",'"')
        self.has_pp_directives = None
        self.keywords = None
        self.lb = None
        self.rb = None
        self.rootMode = None # None, "code" or "doc"

        self.latex_cweb_docs     = c.config.getBool("color_cweb_doc_parts_with_latex")
        self.latex_cweb_comments = c.config.getBool("color_cweb_comments_with_latex")
        # g.pr("docs,comments",self.latex_cweb_docs,self.latex_cweb_comments)
        #@-node:ekr.20031218072017.1606:<< ivars for communication between colorizeAnyLanguage and its allies >>
        #@nl
        #@    << define dispatch dicts >>
        #@+node:ekr.20031218072017.1607:<< define dispatch dicts >>
        self.state_dict = {
            "blockComment" : self.continueBlockComment,
            "doubleString" : self.continueDoubleString, # 1/25/03
            "nocolor"      : self.continueNocolor,
            "normal"       : self.doNormalState,
            "singleString" : self.continueSingleString,  # 1/25/03
            "string3s"     : self.continueSinglePythonString,
            "string3d"     : self.continueDoublePythonString,
            "doc"          : self.continueDocPart,
            "unknown"      : self.doNormalState, # 8/25/05
        }
        #@-node:ekr.20031218072017.1607:<< define dispatch dicts >>
        #@nl
        self.setFontFromConfig()
    #@+node:ekr.20080704085627.3:splitList
    def splitList (self,ivar,fileName):

        '''Process lines containing pairs of entries 
        in a list whose *name* is ivar.
        Put the results in ivars whose names are ivar1 and ivar2.'''

        result1 = [] ; result2 = []
        aList = getattr(self,ivar)

        # Look for pairs.  Comments have already been removed.
        for s in aList:
            pair = s.split(' ')
            if len(pair) == 2 and pair[0].strip() and pair[1].strip():
                result1.append(pair[0].strip())
                result2.append(pair[1].strip())
            else:
                g.es_print('%s: ignoring line: %s' % (fileName,s))

        # Set the ivars.
        name1 = '%s1' % ivar
        name2 = '%s1' % ivar
        setattr(self,name1, result1)
        setattr(self,name2, result2)

        # g.trace(name1,getattr(self,name1))
        # g.trace(name2,getattr(self,name2))
    #@-node:ekr.20080704085627.3:splitList
    #@-node:ekr.20031218072017.1605:color.__init__ & helper
    #@+node:ekr.20031218072017.2801:colorize & recolor_range
    # The main colorizer entry point.

    def colorize(self,p,incremental=False,interruptable=True):
        # interruptable used only in new colorizer.

        # g.trace(g.callers())

        if self.enabled:
            # if self.trace: g.trace("incremental",incremental)
            self.incremental=incremental
            self.updateSyntaxColorer(p)
            return self.colorizeAnyLanguage(p)
        else:
            return "ok" # For unit testing.

    #@-node:ekr.20031218072017.2801:colorize & recolor_range
    #@+node:ekr.20031218072017.1880:colorizeAnyLanguage & allies
    def colorizeAnyLanguage (self,p,leading=None,trailing=None):

        """Color the body pane either incrementally or non-incrementally"""

        c = self.c ; w = c.frame.body.bodyCtrl

        if not c.config.getBool('use_syntax_coloring'):
            # There have been reports of this trace causing crashes.
            # Certainly it is not necessary.
            # g.trace('no coloring')
            return

        if self.killFlag:
            self.removeAllTags()
            return
        try:
            # g.trace('incremental',self.incremental)
            #@        << initialize ivars & tags >>
            #@+node:ekr.20031218072017.1602:<< initialize ivars & tags >> colorizeAnyLanguage
            # Copy the arguments.
            self.p = p

            # Get the body text, converted to unicode.
            self.allBodyText = w.getAllText()
            sel = w.getInsertPoint()
            start,end = g.convertPythonIndexToRowCol(self.allBodyText,sel)
            start += 1 # Simulate the old 1-based Tk scheme.  self.index undoes this hack.
            # g.trace('new',start,end)

            if self.language: self.language = self.language.lower()
            # g.trace(self.count,self.p)
            # g.trace(body.tag_names())

            if not self.incremental:
                self.removeAllTags()
                # self.removeAllImages()

            #@<< configure fonts >>
            #@+node:ekr.20060829084924:<< configure fonts >> (revise,maybe)
            # Get the default body font.
            defaultBodyfont = self.fonts.get('default_body_font')
            if not defaultBodyfont:
                defaultBodyfont = c.config.getFontFromParams(
                    "body_text_font_family", "body_text_font_size",
                    "body_text_font_slant",  "body_text_font_weight",
                    c.config.defaultBodyFontSize)
                self.fonts['default_body_font'] = defaultBodyfont

            # Configure fonts.
            w = c.frame.body.bodyCtrl
            keys = sorted(default_font_dict)
            for key in keys:
                option_name = default_font_dict[key]
                # First, look for the language-specific setting, then the general setting.
                for name in ('%s_%s' % (self.language,option_name),(option_name)):
                    font = self.fonts.get(name)
                    if font:
                        # g.trace('found',name,id(font))
                        w.tag_config(key,font=font)
                        break
                    else:
                        family = c.config.get(name + '_family','family')
                        size   = c.config.get(name + '_size',  'size')   
                        slant  = c.config.get(name + '_slant', 'slant')
                        weight = c.config.get(name + '_weight','weight')
                        if family or slant or weight or size:
                            family = family or g.app.config.defaultFontFamily
                            size   = size or str(c.config.defaultBodyFontSize)
                            slant  = slant or 'roman'
                            weight = weight or 'normal'
                            font = c.config.getFontFromParams(family,size,slant,weight)
                            # Save a reference to the font so it 'sticks'.
                            self.fonts[name] = font 
                            # g.trace(key,name,family,size,slant,weight,id(font))
                            w.tag_config(key,font=font)
                            break
                else: # Neither the general setting nor the language-specific setting exists.
                    if len(list(self.fonts.keys())) > 1: # Restore the default font.
                        # g.trace('default',key)
                        w.tag_config(key,font=defaultBodyfont)
            #@-node:ekr.20060829084924:<< configure fonts >> (revise,maybe)
            #@nl
            #@<< configure tags >>
            #@+node:ekr.20031218072017.1603:<< configure tags >>
            # g.trace('configure tags',self.c.frame.body.bodyCtrl)

            for name in default_colors_dict:
                option_name,default_color = default_colors_dict[name]
                option_color = c.config.getColor(option_name)
                color = g.choose(option_color,option_color,default_color)
                # g.trace(name,color)
                # Must use foreground, not fg.
                try:
                    c.frame.body.tag_configure(name, foreground=color)
                except: # Recover after a user error.
                    c.frame.body.tag_configure(name, foreground=default_color)

            underline_undefined = c.config.getBool("underline_undefined_section_names")
            use_hyperlinks      = c.config.getBool("use_hyperlinks")
            self.use_hyperlinks = use_hyperlinks

            # underline=var doesn't seem to work.
            if 0: # use_hyperlinks: # Use the same coloring, even when hyperlinks are in effect.
                c.frame.body.tag_configure("link",underline=1) # defined
                c.frame.body.tag_configure("name",underline=0) # undefined
            else:
                c.frame.body.tag_configure("link",underline=0)
                if underline_undefined:
                    c.frame.body.tag_configure("name",underline=1)
                else:
                    c.frame.body.tag_configure("name",underline=0)

            # 8/4/02: we only create tags for whitespace when showing invisibles.
            if self.showInvisibles:
                for name,option_name,default_color in (
                    ("blank","show_invisibles_space_background_color","Gray90"),
                    ("tab",  "show_invisibles_tab_background_color",  "Gray80")):
                    option_color = c.config.getColor(option_name)
                    color = g.choose(option_color,option_color,default_color)
                    try:
                        c.frame.body.tag_configure(name,background=color)
                    except: # Recover after a user error.
                        c.frame.body.tag_configure(name,background=default_color)

            # 11/15/02: Colors for latex characters.  Should be user options...

            if 1: # Alas, the selection doesn't show if a background color is specified.
                c.frame.body.tag_configure("latexModeBackground",foreground="black")
                c.frame.body.tag_configure("latexModeKeyword",foreground="blue")
                c.frame.body.tag_configure("latexBackground",foreground="black")
                c.frame.body.tag_configure("latexKeyword",foreground="blue")
            else: # Looks cool, and good for debugging.
                c.frame.body.tag_configure("latexModeBackground",foreground="black",background="seashell1")
                c.frame.body.tag_configure("latexModeKeyword",foreground="blue",background="seashell1")
                c.frame.body.tag_configure("latexBackground",foreground="black",background="white")
                c.frame.body.tag_configure("latexKeyword",foreground="blue",background="white")

            # Tags for wiki coloring.
            if self.showInvisibles:
                c.frame.body.tag_configure("elide",background="yellow")
            else:
                c.frame.body.tag_configure("elide",elide="1")
            c.frame.body.tag_configure("bold",font=self.bold_font)
            c.frame.body.tag_configure("italic",font=self.italic_font)
            c.frame.body.tag_configure("bolditalic",font=self.bolditalic_font)
            for name in self.color_tags_list:
                c.frame.body.tag_configure(name,foreground=name)
            #@-node:ekr.20031218072017.1603:<< configure tags >>
            #@nl
            #@<< configure language-specific settings >>
            #@+node:ekr.20031218072017.370:<< configure language-specific settings >> colorizer
            # Define has_string, keywords, single_comment_start, block_comment_start, block_comment_end.

            if self.language == "cweb": # Use C comments, not cweb sentinel comments.
                delim1,delim2,delim3 = g.set_delims_from_language("c")
            elif self.comment_string:
                delim1,delim2,delim3 = g.set_delims_from_string(self.comment_string)
            elif self.language == "plain": # 1/30/03
                delim1,delim2,delim3 = None,None,None
            else:
                delim1,delim2,delim3 = g.set_delims_from_language(self.language)

            self.single_comment_start = delim1
            self.block_comment_start = delim2
            self.block_comment_end = delim3

            # A strong case can be made for making this code as fast as possible.
            # Whether this is compatible with general language descriptions remains to be seen.
            self.case_sensitiveLanguage = self.language not in case_insensitiveLanguages
            self.has_string = self.language != "plain"
            if self.language == "plain":
                self.string_delims = ()
            elif self.language in ("elisp","html"):
                self.string_delims = ('"')
            else:
                self.string_delims = ("'",'"')
            self.has_pp_directives = self.language in ("c","csharp","cweb","latex")

            # The list of languages for which keywords exist.
            # Eventually we might just use language_delims_dict.keys()
            languages = [
                "actionscript","ada","c","csharp","css","cweb","elisp","html","java","latex","lua",
                "pascal","perl","perlpod","php","plsql","python","rapidq","rebol","ruby","shell","tcltk"]

            self.keywords = []
            if self.language == "cweb":
                for i in self.c_keywords:
                    self.keywords.append(i)
                for i in self.cweb_keywords:
                    self.keywords.append(i)
            else:
                for name in languages:
                    if self.language==name: 
                        # g.trace("setting keywords for",name)
                        self.keywords = getattr(self, name + "_keywords")

            # Color plain text unless we are under the control of @nocolor.
            # state = g.choose(self.flag,"normal","nocolor")
            state = self.setFirstLineState()

            if 1: # 10/25/02: we color both kinds of references in cweb mode.
                self.lb = "<<"
                self.rb = ">>"
            else:
                self.lb = g.choose(self.language == "cweb","@<","<<")
                self.rb = g.choose(self.language == "cweb","@>",">>")
            #@-node:ekr.20031218072017.370:<< configure language-specific settings >> colorizer
            #@nl

            self.hyperCount = 0 # Number of hypertext tags
            self.count += 1
            lines = self.allBodyText.split('\n')
            #@-node:ekr.20031218072017.1602:<< initialize ivars & tags >> colorizeAnyLanguage
            #@nl
            g.doHook("init-color-markup",colorer=self,p=self.p,v=self.p)
            if self.incremental and (
                #@            << all state ivars match >>
                #@+node:ekr.20031218072017.1881:<< all state ivars match >>
                self.flag == self.last_flag and
                self.last_language == self.language
                #@-node:ekr.20031218072017.1881:<< all state ivars match >>
                #@afterref
 ):
                #@            << incrementally color the text >>
                #@+node:ekr.20031218072017.1882:<< incrementally color the text >>
                #@+at  
                #@nonl
                # Each line has a starting state.  The starting 
                # state for the first line is always "normal".
                # 
                # We need remember only self.lines and self.states 
                # between colorizing.  It is not necessary to know 
                # where the text comes from, only what the previous 
                # text was!  We must always colorize everything when 
                # changing nodes, even if all lines match, because 
                # the context may be different.
                # 
                # We compute the range of lines to be recolored by 
                # comparing leading lines and trailing lines of old 
                # and new text.  All other lines (the middle lines) 
                # must be colorized, as well as any trailing lines 
                # whose states may have changed as the result of 
                # changes to the middle lines.
                #@-at
                #@@c

                if self.trace: g.trace("incremental",self.language)

                # 6/30/03: make a copies of everything
                old_lines = self.lines[:]
                old_states = self.states[:]
                new_lines = lines[:]
                new_states = []

                new_len = len(new_lines)
                old_len = len(old_lines)

                if new_len == 0:
                    self.states = []
                    self.lines = []
                    return

                # Bug fix: 11/21/02: must test against None.
                if leading != None and trailing != None:
                    # g.pr("leading,trailing:",leading,trailing)
                    leading_lines = leading
                    trailing_lines = trailing
                else:
                    #@    << compute leading, middle & trailing lines >>
                    #@+node:ekr.20031218072017.1883:<< compute leading, middle & trailing  lines >>
                    #@+at 
                    #@nonl
                    # The leading lines are the leading matching 
                    # lines.  The trailing lines are the trailing 
                    # matching lines.  The middle lines are all 
                    # other new lines.  We will color at least all 
                    # the middle lines.  There may be no middle 
                    # lines if we delete lines.
                    #@-at
                    #@@c

                    min_len = min(old_len,new_len)

                    i = 0
                    while i < min_len:
                        if old_lines[i] != new_lines[i]:
                            break
                        i += 1
                    leading_lines = i

                    if leading_lines == new_len:
                        # All lines match, and we must color _everything_.
                        # (several routine delete, then insert the text again,
                        # deleting all tags in the process).
                        # g.pr("recolor all")
                        leading_lines = trailing_lines = 0
                    else:
                        i = 0
                        while i < min_len - leading_lines:
                            if old_lines[old_len-i-1] != new_lines[new_len-i-1]:
                                break
                            i += 1
                        trailing_lines = i
                    #@-node:ekr.20031218072017.1883:<< compute leading, middle & trailing  lines >>
                    #@nl

                middle_lines = new_len - leading_lines - trailing_lines
                # g.pr("middle lines", middle_lines)

                #@<< clear leading_lines if middle lines involve @color or @recolor  >>
                #@+node:ekr.20031218072017.1884:<< clear leading_lines if middle lines involve @color or @recolor  >>
                #@+at 
                #@nonl
                # 11/19/02: Changing @color or @nocolor directives 
                # requires we recolor all leading states as well.
                #@-at
                #@@c

                if trailing_lines == 0:
                    m1 = new_lines[leading_lines:]
                    m2 = old_lines[leading_lines:]
                else:
                    m1 = new_lines[leading_lines:-trailing_lines]
                    m2 = old_lines[leading_lines:-trailing_lines]
                m1.extend(m2) # m1 now contains all old and new middle lines.
                if m1:
                    for s in m1:
                        ### s = g.toUnicode(s)
                        i = g.skip_ws(s,0)
                        if g.match_word(s,i,"@color") or g.match_word(s,i,"@nocolor"):
                            leading_lines = 0
                            break
                #@-node:ekr.20031218072017.1884:<< clear leading_lines if middle lines involve @color or @recolor  >>
                #@nl
                #@<< initialize new states >>
                #@+node:ekr.20031218072017.1885:<< initialize new states >>
                # Copy the leading states from the old to the new lines.
                i = 0
                while i < leading_lines and i < old_len: # 12/8/02
                    new_states.append(old_states[i])
                    i += 1

                # We know the starting state of the first middle line!
                if middle_lines > 0 and i < old_len:
                    new_states.append(old_states[i])
                    i += 1

                # Set the state of all other middle lines to "unknown".
                first_trailing_line = max(0,new_len - trailing_lines)
                while i < first_trailing_line:
                    new_states.append("unknown")
                    i += 1

                # Copy the trailing states from the old to the new lines.
                i = max(0,old_len - trailing_lines)
                while i < old_len and i < len(old_states):
                    new_states.append(old_states[i])
                    i += 1

                # 1/8/03: complete new_states by brute force.
                while len(new_states) < new_len:
                    new_states.append("unknown")
                #@-node:ekr.20031218072017.1885:<< initialize new states >>
                #@nl
                #@<< colorize until the states match >>
                #@+node:ekr.20031218072017.1886:<< colorize until the states match >>
                # Colorize until the states match.
                # All middle lines have "unknown" state, so they will all be colored.

                # Start in the state _after_ the last leading line, which may be unknown.
                i = leading_lines
                while i > 0:
                    if i < old_len and i < new_len:
                        state = new_states[i]
                        # assert(state!="unknown") # This can fail.
                        break
                    else:
                        i -= 1

                if i == 0:
                    # Color plain text unless we are under the control of @nocolor.
                    # state = g.choose(self.flag,"normal","nocolor")
                    state = self.setFirstLineState()
                    new_states[0] = state

                # The new_states[] will be "unknown" unless the lines match,
                # so we do not need to compare lines here.
                while i < new_len:
                    self.line_index = i + 1
                    state = self.colorizeLine(new_lines[i],state)
                    i += 1
                    # Set the state of the _next_ line.
                    if i < new_len and state != new_states[i]:
                        new_states[i] = state
                    else: break

                # Update the ivars
                self.states = new_states
                self.lines = new_lines
                #@-node:ekr.20031218072017.1886:<< colorize until the states match >>
                #@nl
                #@-node:ekr.20031218072017.1882:<< incrementally color the text >>
                #@nl
            else:
                #@            << non-incrementally color the text >>
                #@+node:ekr.20031218072017.1887:<< non-incrementally color the text >>
                if self.trace: g.trace("non-incremental",self.language)

                self.line_index = 1 # The Tk line number for indices, as in n.i
                for s in lines:
                    state = self.colorizeLine(s,state)
                    self.line_index += 1
                #@-node:ekr.20031218072017.1887:<< non-incrementally color the text >>
                #@nl
            #@        << update state ivars >>
            #@+node:ekr.20031218072017.1888:<< update state ivars >>
            self.last_flag = self.flag
            self.last_language = self.language
            #@-node:ekr.20031218072017.1888:<< update state ivars >>
            #@nl
            return "ok" # for testing.
        except:
            #@        << set state ivars to "unknown" >>
            #@+node:ekr.20031218072017.1889:<< set state ivars to "unknown" >>
            self.last_flag = "unknown"
            self.last_language = "unknown"
            #@-node:ekr.20031218072017.1889:<< set state ivars to "unknown" >>
            #@nl
            if self.c:
                g.es_exception()
            else:
                import traceback ; traceback.print_exc()
            return "error" # for unit testing.
    #@-node:ekr.20031218072017.1880:colorizeAnyLanguage & allies
    #@+node:ekr.20031218072017.1892:colorizeLine & allies
    def colorizeLine (self,s,state):

        # g.pr("line,inc,state,s:",self.line_index,self.incremental,state,s)

        ### s = g.toUnicode(s)

        if self.incremental:
            self.removeTagsFromLine()

        i = 0
        while i < len(s):
            self.progress = i
            func = self.state_dict[state]
            i,state = func(s,i)

        return state
    #@+node:ekr.20031218072017.1618:continueBlockComment
    def continueBlockComment (self,s,i):

        j = s.find(self.block_comment_end,i)

        if j == -1:
            j = len(s) # The entire line is part of the block comment.
            if self.language=="cweb":
                self.doLatexLine(s,i,j)
            else:
                if not g.doHook("color-optional-markup",
                    colorer=self,p=self.p,v=self.p,s=s,i=i,j=j,colortag="comment"):
                    self.tag("comment",i,j)
            return j,"blockComment" # skip the rest of the line.

        else:
            # End the block comment.
            k = len(self.block_comment_end)
            if self.language=="cweb" and self.latex_cweb_comments:
                self.doLatexLine(s,i,j)
                self.tag("comment",j,j+k)
            else:
                if not g.doHook("color-optional-markup",
                    colorer=self,p=self.p,v=self.p,s=s,i=i,j=j+k,colortag="comment"):
                    self.tag("comment",i,j+k)
            i = j + k
            return i,"normal"
    #@-node:ekr.20031218072017.1618:continueBlockComment
    #@+node:ekr.20031218072017.1893:continueSingle/DoubleString
    def continueDoubleString (self,s,i):
        return self.continueString(s,i,'"',"doubleString")

    def continueSingleString (self,s,i):
        return self.continueString(s,i,"'","singleString")

    # Similar to skip_string.
    def continueString (self,s,i,delim,continueState):
        # g.trace(delim + s[i:])
        continueFlag = g.choose(self.language in ("elisp","html"),True,False)
        j = i
        while i < len(s) and s[i] != delim:
            if s[i:] == "\\":
                i = len(s) ; continueFlag = True ; break
            elif s[i] == "\\":
                i += 2
            else:
                i += 1
        if i >= len(s):
            i = len(s)
        elif s[i] == delim:
            i += 1 ; continueFlag = False
        self.tag("string",j,i)
        state = g.choose(continueFlag,continueState,"normal")
        return i,state
    #@-node:ekr.20031218072017.1893:continueSingle/DoubleString
    #@+node:ekr.20031218072017.1614:continueDocPart
    def continueDocPart (self,s,i):

        c = self.c ; state = "doc"
        if self.language == "cweb":
            #@        << handle cweb doc part >>
            #@+node:ekr.20031218072017.1615:<< handle cweb doc part >>
            word = self.getCwebWord(s,i)
            if word and len(word) > 0:
                j = i + len(word)
                if word in ("@<","@(","@c","@d","@f","@p"):
                    state = "normal" # end the doc part and rescan
                else:
                    # The control code does not end the doc part.
                    self.tag("keyword",i,j)
                    i = j
                    if word in ("@^","@.","@:","@="): # Ended by "@>"
                        j = s.find("@>",i)
                        if j > -1:
                            self.tag("cwebName",i,j)
                            self.tag("nameBrackets",j,j+2)
                            i = j + 2
            elif g.match(s,i,self.lb):
                j = self.doNowebSecRef(s,i)
                if j == i + 2: # not a section ref.
                    self.tag("docPart",i,j)
                i = j
            elif self.latex_cweb_docs:
                # Everything up to the next "@" is latex colored.
                j = s.find("@",i+1)
                if j == -1: j = len(s)
                self.doLatexLine(s,i,j)
                i = j
            else:
                # Everthing up to the next "@" is in the doc part.
                j = s.find("@",i+1)
                if j == -1: j = len(s)
                self.tag("docPart",i,j)
                i = j
            #@-node:ekr.20031218072017.1615:<< handle cweb doc part >>
            #@nl
        else:
            #@        << handle noweb doc part >>
            #@+node:ekr.20031218072017.1616:<< handle noweb doc part >>
            if i == 0 and g.match(s,i,"<<"):
                # Possible section definition line.
                return i,"normal" # rescan the line.

            if i == 0 and s[i] == '@':
                j = self.skip_id(s,i+1,chars='-')
                word = s[i:j]
                word = word.lower()
            else:
                word = ""

            if word in ["@c","@code","@unit","@root","@root-code","@root-doc","@color","@nocolor"]:
                # End of the doc part.
                c.frame.body.tag_remove("docPart",self.index(i),self.index(j)) # 10/27/03
                self.tag("leoKeyword",i,j)
                state = "normal"
                if word != '@nocolor': i = j # 3/8/05: Rescan @nocolor.
            else:
                # The entire line is in the doc part.
                j = len(s)
                if not g.doHook("color-optional-markup",
                    colorer=self,p=self.p,v=self.p,s=s,i=i,j=j,colortag="docPart"):
                    self.tag("docPart",i,j)
                i = j # skip the rest of the line.
            #@-node:ekr.20031218072017.1616:<< handle noweb doc part >>
            #@nl
        return i,state
    #@-node:ekr.20031218072017.1614:continueDocPart
    #@+node:ekr.20031218072017.1894:continueNocolor
    def continueNocolor (self,s,i):

        if i == 0 and s[i] == '@':
            j = self.skip_id(s,i+1)
            word = s[i:j]
            word = word.lower()
        else:
            word = ""

        if word == "@color" and self.language != "plain":
            # End of the nocolor part.
            self.tag("leoKeyword",0,j)
            return i,"normal"
        else:
            # The entire line is in the nocolor part.
            # Add tags for blanks and tabs to make "Show Invisibles" work.
            for ch in s[i:]:
                if ch == ' ':
                    self.tag("blank",i,i+1)
                elif ch == '\t':
                    self.tag("tab",i,i+1)
                i += 1
            return i,"nocolor"
    #@-node:ekr.20031218072017.1894:continueNocolor
    #@+node:ekr.20031218072017.1613:continueSingle/DoublePythonString
    def continueDoublePythonString (self,s,i):
        j = s.find('"""',i)
        return self.continuePythonString(s,i,j,"string3d")

    def continueSinglePythonString (self,s,i):
        j = s.find("'''",i)
        return self.continuePythonString(s,i,j,"string3s")

    def continuePythonString (self,s,i,j,continueState):

        if j == -1: # The entire line is part of the triple-quoted string.
            j = len(s)
            if continueState == "string3d":
                if not g.doHook("color-optional-markup",
                    colorer=self,p=self.p,v=self.p,s=s,i=i,j=j,colortag="string"):
                    self.tag("string",i,j)
            else:
                self.tag("string",i,j)
            return j,continueState # skip the rest of the line.

        else: # End the string
            if continueState == "string3d":
                if not g.doHook("color-optional-markup",
                    colorer=self,p=self.p,v=self.p,s=s,i=i,j=j,colortag="string"):
                    self.tag("string",i,j+3)
                else:
                    self.tag("string",i,j+3)
            else:
                self.tag("string",i,j+3)
            return j+3,"normal"
    #@-node:ekr.20031218072017.1613:continueSingle/DoublePythonString
    #@+node:ekr.20031218072017.1620:doAtKeyword: NOT for cweb keywords
    # Handles non-cweb keyword.

    def doAtKeyword (self,s,i):

        j = self.skip_id(s,i+1,chars="-") # to handle @root-code, @root-doc
        word = s[i:j]
        word = word.lower()
        # g.trace(word,word[1:] in g.globalDirectiveList)
        if i != 0 and word not in ("@others","@all"):
            word = "" # can't be a Leo keyword, even if it looks like it.

        # 7/8/02: don't color doc parts in plain text.
        if self.language != "plain" and (word == "@" or word == "@doc"):
            # at-space is a Leo keyword.
            self.tag("leoKeyword",i,j)
            k = len(s) # Everything on the line is in the doc part.
            if not g.doHook("color-optional-markup",
                colorer=self,p=self.p,v=self.p,s=s,i=j,j=k,colortag="docPart"):
                self.tag("docPart",j,k)
            return k,"doc"
        elif word == "@nocolor":
            # Nothing on the line is colored.
            self.tag("leoKeyword",i,j)
            return j,"nocolor"
        elif word[1:] in g.globalDirectiveList:
            self.tag("leoKeyword",i,j)
            return j,"normal"
        else:
            return j,"normal"
    #@-node:ekr.20031218072017.1620:doAtKeyword: NOT for cweb keywords
    #@+node:ekr.20031218072017.1895:doLatexLine
    # Colorize the line from i to j.

    def doLatexLine (self,s,i,j):

        while i < j:
            if g.match(s,i,"\\"):
                k = self.skip_id(s,i+1)
                word = s[i:k]
                if word in self.latex_keywords:
                    self.tag("latexModeKeyword",i,k)
                i = k
            else:
                self.tag("latexModeBackground",i,i+1)
                i += 1
    #@-node:ekr.20031218072017.1895:doLatexLine
    #@+node:ekr.20031218072017.1896:doNormalState
    def doNormalState (self,s,i):

        ch = s[i] ; state = "normal"

        if ch in string.ascii_letters or ch == '_' or (
            (ch == '\\' and self.language=="latex") or
            (ch in '/&<>' and self.language=="html") or
            (ch == '$' and self.language=="rapidq")
        ):
            #@        << handle possible keyword >>
            #@+middle:ekr.20031218072017.1897:Valid regardless of latex mode
            #@+node:ekr.20031218072017.1898:<< handle possible  keyword >>
            if self.language == "latex":
                #@    << handle possible latex keyword >>
                #@+node:ekr.20031218072017.1899:<< handle possible latex keyword >>
                if g.match(s,i,"\\"):
                    if i + 1 < len(s) and s[i+1] in self.latex_special_keyword_characters:
                        j = i + 2 # A special 2-character LaTex keyword.
                    else:
                        j = self.skip_id(s,i+1)
                    word = s[i:j]
                    if word in self.latex_keywords:
                        self.tag("latexKeyword",i,j)
                    else:
                        self.tag("latexBackground",i,j)
                else:
                    self.tag("latexBackground",i,i+1)
                    j = i + 1 # skip the character.
                #@-node:ekr.20031218072017.1899:<< handle possible latex keyword >>
                #@nl
            elif self.language == "html":
                #@    << handle possible html keyword >>
                #@+node:ekr.20031218072017.1900:<< handle possible html keyword >>
                if g.match(s,i,"<!---") or g.match(s,i,"<!--"):
                    if g.match(s,i,"<!---"): k = 5
                    else: k = 4
                    self.tag("comment",i,i+k)
                    j = i + k ; state = "blockComment"
                elif g.match(s,i,"<"):
                    if g.match(s,i,"</"): k = 2
                    else: k = 1
                    j = self.skip_id(s,i+k)
                    self.tag("keyword",i,j)
                elif g.match(s,i,"&"):
                    j = self.skip_id(s,i+1,';')
                    self.tag("keyword",i,j)
                elif g.match(s,i,"/>"):
                    j = i + 2
                    self.tag("keyword",i,j)
                elif g.match(s,i,">"):
                    j = i + 1
                    self.tag("keyword",i,j)
                else:
                    j = i + 1
                #@-node:ekr.20031218072017.1900:<< handle possible html keyword >>
                #@nl
            else:
                #@    << handle general keyword >>
                #@+node:ekr.20031218072017.1901:<< handle general keyword >>
                if self.language == "rapidq":
                    j = self.skip_id(s,i+1,chars="$")
                elif self.language == "rebol":
                    j = self.skip_id(s,i+1,chars="-~!?")
                elif self.language in ("elisp","css"):
                    j = self.skip_id(s,i+1,chars="-")
                else:
                    j = self.skip_id(s,i)

                word = s[i:j]
                if not self.case_sensitiveLanguage:
                    word = word.lower()

                if word in self.keywords:
                    self.tag("keyword",i,j)
                elif self.language == "php":
                    if word in self.php_paren_keywords and g.match(s,j,"()"):
                        self.tag("keyword",i,j+2)
                        j += 2
                #@-node:ekr.20031218072017.1901:<< handle general keyword >>
                #@nl
            i = j
            #@-node:ekr.20031218072017.1898:<< handle possible  keyword >>
            #@-middle:ekr.20031218072017.1897:Valid regardless of latex mode
            #@nl
        elif g.match(s,i,self.lb):
            i = self.doNowebSecRef(s,i)
        elif ch == '@':
            #@        << handle at keyword >>
            #@+middle:ekr.20031218072017.1897:Valid regardless of latex mode
            #@+node:ekr.20031218072017.1902:<< handle at keyword >>
            if self.language == "cweb":
                if g.match(s,i,"@(") or g.match(s,i,"@<"):
                    #@        << handle cweb ref or def >>
                    #@+node:ekr.20031218072017.1904:<< handle cweb ref or def >>
                    self.tag("nameBrackets",i,i+2)

                    # See if the line contains the right name bracket.
                    j = s.find("@>=",i+2)
                    k = g.choose(j==-1,2,3)
                    if j == -1:
                        j = s.find("@>",i+2)

                    if j == -1:
                        i += 2
                    else:
                        self.tag("cwebName",i+2,j)
                        self.tag("nameBrackets",j,j+k)
                        i = j + k
                    #@-node:ekr.20031218072017.1904:<< handle cweb ref or def >>
                    #@nl
                else:
                    word = self.getCwebWord(s,i)
                    if word:
                        #@            << Handle cweb control word >>
                        #@+node:ekr.20031218072017.1903:<< Handle cweb control word >>
                        # Color and skip the word.
                        assert(self.language=="cweb")

                        j = i + len(word)
                        self.tag("keyword",i,j)
                        i = j

                        if word in ("@ ","@\t","@\n","@*","@**"):
                            state = "doc"
                        elif word in ("@<","@(","@c","@d","@f","@p"):
                            state = "normal"
                        elif word in ("@^","@.","@:","@="): # Ended by "@>"
                            j = s.find("@>",i)
                            if j > -1:
                                self.tag("cwebName",i,j)
                                self.tag("nameBrackets",j,j+2)
                                i = j + 2
                        #@-node:ekr.20031218072017.1903:<< Handle cweb control word >>
                        #@nl
                    else:
                        i,state = self.doAtKeyword(s,i)
            else:
                i,state = self.doAtKeyword(s,i)
            #@-node:ekr.20031218072017.1902:<< handle at keyword >>
            #@-middle:ekr.20031218072017.1897:Valid regardless of latex mode
            #@nl
        elif g.match(s,i,self.single_comment_start):
            #@        << handle single-line comment >>
            #@+middle:ekr.20031218072017.1897:Valid regardless of latex mode
            #@+node:ekr.20031218072017.1617:<< handle single-line comment >>
            # g.pr("single-line comment i,s:",i,s)

            if self.language == "cweb" and self.latex_cweb_comments:
                j = i + len(self.single_comment_start)
                self.tag("comment",i,j)
                self.doLatexLine(s,j,len(s))
                i = len(s)
            elif self.language == "shell" and (i>0 and s[i-1]=='$'):
                i += 1 # '$#' in shell should not start a comment (DS 040113)
            else:
                j = len(s)
                if not g.doHook("color-optional-markup",
                    colorer=self,p=self.p,v=self.p,s=s,i=i,j=j,colortag="comment"):
                    self.tag("comment",i,j)
                i = j
            #@-node:ekr.20031218072017.1617:<< handle single-line comment >>
            #@-middle:ekr.20031218072017.1897:Valid regardless of latex mode
            #@nl
        elif g.match(s,i,self.block_comment_start):
            #@        << start block comment >>
            #@+middle:ekr.20031218072017.1897:Valid regardless of latex mode
            #@+node:ekr.20031218072017.1619:<< start block comment >>
            k = len(self.block_comment_start)

            if not g.doHook("color-optional-markup",
                colorer=self,p=self.p,v=self.p,s=s,i=i,j=i+k,colortag="comment"):
                self.tag("comment",i,i+k)

            i += k ; state = "blockComment"
            #@-node:ekr.20031218072017.1619:<< start block comment >>
            #@-middle:ekr.20031218072017.1897:Valid regardless of latex mode
            #@nl
        elif ch == '%' and self.language=="cweb":
            #@        << handle latex line >>
            #@+middle:ekr.20031218072017.1897:Valid regardless of latex mode
            #@+node:ekr.20031218072017.1905:<< handle latex line >>
            self.tag("keyword",i,i+1)
            i += 1 # Skip the %
            self.doLatexLine(s,i,len(s))
            i = len(s)
            #@-node:ekr.20031218072017.1905:<< handle latex line >>
            #@-middle:ekr.20031218072017.1897:Valid regardless of latex mode
            #@nl
        elif self.language=="latex":
            #@        << handle latex normal character >>
            #@+middle:ekr.20031218072017.1906:Vaid only in latex mode
            #@+node:ekr.20031218072017.1907:<< handle latex normal character >>
            if self.language=="cweb":
                self.tag("latexModeBackground",i,i+1)
            else:
                self.tag("latexBackground",i,i+1)
            i += 1
            #@-node:ekr.20031218072017.1907:<< handle latex normal character >>
            #@-middle:ekr.20031218072017.1906:Vaid only in latex mode
            #@nl
        # ---- From here on self.language != "latex" -----
        elif ch in self.string_delims:
            #@        << handle string >>
            #@+middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@+node:ekr.20031218072017.1612:<< handle string >>
            # g.trace(self.language)

            if self.language == "python":

                delim = s[i:i+3]
                j, state = self.skip_python_string(s,i)
                if delim == '"""':
                    # Only handle wiki items in """ strings.
                    if not g.doHook("color-optional-markup",
                        colorer=self,p=self.p,v=self.p,s=s,i=i,j=j,colortag="string"):
                        self.tag("string",i,j)
                else:
                    self.tag("string",i,j)
                i = j

            else:
                j, state = self.skip_string(s,i)
                self.tag("string",i,j)
                i = j
            #@-node:ekr.20031218072017.1612:<< handle string >>
            #@-middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@nl
        elif ch == '#' and self.has_pp_directives:
            #@        << handle C preprocessor line >>
            #@+middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@+node:ekr.20031218072017.1909:<< handle C preprocessor line >>
            # 10/17/02: recognize comments in preprocessor lines.
            j = i
            while i < len(s):
                if g.match(s,i,self.single_comment_start) or g.match(s,i,self.block_comment_start):
                    break
                else: i += 1

            self.tag("pp",j,i)
            #@-node:ekr.20031218072017.1909:<< handle C preprocessor line >>
            #@-middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@nl
        elif self.language == "php" and (g.match(s,i,"<") or g.match(s,i,"?")):
            # g.trace("%3d" % i,php_re.match(s,i),s)
            #@        << handle special php keywords >>
            #@+middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@+node:ekr.20031218072017.1910:<< handle special php keywords >>
            if g.match(s.lower(),i,"<?php"):
                self.tag("keyword",i,i+5)
                i += 5
            elif g.match(s,i,"?>"):
                self.tag("keyword",i,i+2)
                i += 2
            else:
                i += 1
            #@-node:ekr.20031218072017.1910:<< handle special php keywords >>
            #@-middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@nl
        elif ch == ' ':
            #@        << handle blank >>
            #@+middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@+node:ekr.20031218072017.1911:<< handle blank >>
            if self.showInvisibles:
                self.tag("blank",i,i+1)
            i += 1
            #@-node:ekr.20031218072017.1911:<< handle blank >>
            #@-middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@nl
        elif ch == '\t':
            #@        << handle tab >>
            #@+middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@+node:ekr.20031218072017.1912:<< handle tab >>
            if self.showInvisibles:
                self.tag("tab",i,i+1)
            i += 1
            #@-node:ekr.20031218072017.1912:<< handle tab >>
            #@-middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@nl
        else:
            #@        << handle normal character >>
            #@+middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@+node:ekr.20031218072017.1913:<< handle normal character >>
            # self.tag("normal",i,i+1)
            i += 1
            #@-node:ekr.20031218072017.1913:<< handle normal character >>
            #@-middle:ekr.20031218072017.1908:Valid when not in latex_mode
            #@nl

        if 0: # This can fail harmlessly when using wxPython plugin.  Don't know exactly why.
            g.trace(self.progress,i,state)
            assert(self.progress < i)
        return i,state
    #@+node:ekr.20031218072017.1897:Valid regardless of latex mode
    #@-node:ekr.20031218072017.1897:Valid regardless of latex mode
    #@+node:ekr.20031218072017.1906:Vaid only in latex mode
    #@-node:ekr.20031218072017.1906:Vaid only in latex mode
    #@+node:ekr.20031218072017.1908:Valid when not in latex_mode
    #@-node:ekr.20031218072017.1908:Valid when not in latex_mode
    #@-node:ekr.20031218072017.1896:doNormalState
    #@+node:ekr.20031218072017.1914:doNowebSecRef (colorizer)
    def doNowebSecRef (self,s,i):

        c = self.c
        self.tag("nameBrackets",i,i+2)

        # See if the line contains the right name bracket.
        j = s.find(self.rb+"=",i+2)
        k = g.choose(j==-1,2,3)
        if j == -1:
            j = s.find(self.rb,i+2)
        if j == -1:
            return i + 2
        else:
            # includes brackets
            searchName = s[i:j]
            ref = g.findReference(c,searchName,self.p)
            if ref:
                self.tag("link",i+2,j)
                if self.use_hyperlinks:
                    #@                << set the hyperlink >>
                    #@+node:ekr.20031218072017.1915:<< set the hyperlink >>
                    # Set the bindings to vnode callbacks.
                    # Create the tag.
                    # Create the tag name.
                    tagName = "hyper" + str(self.hyperCount)
                    self.hyperCount += 1
                    c.frame.body.tag_delete(tagName)
                    self.tag(tagName,i+2,j)

                    ref.tagName = tagName
                    w = c.frame.body
                    c.tag_bind(w,tagName,"<Control-1>",ref.OnHyperLinkControlClick)
                    c.tag_bind(w,tagName,"<Any-Enter>",ref.OnHyperLinkEnter)
                    c.tag_bind(w,tagName,"<Any-Leave>",ref.OnHyperLinkLeave)
                    #@-node:ekr.20031218072017.1915:<< set the hyperlink >>
                    #@nl
            elif k == 3: # a section definition
                self.tag("link",i+2,j)
            else:
                self.tag("name",i+2,j)
            self.tag("nameBrackets",j,j+k)
            return j + k
    #@-node:ekr.20031218072017.1914:doNowebSecRef (colorizer)
    #@+node:ekr.20031218072017.1604:removeAllTags & removeTagsFromLines
    def removeAllTags (self):

        # Warning: the following DOES NOT WORK: w.tag_delete(self.tags)
        w = self.c.frame.body
        for tag in self.tags:
            w.tag_delete(tag)

        for tag in self.color_tags_list:
            w.tag_delete(tag)

    def removeTagsFromLine (self):

        # g.pr("removeTagsFromLine",self.line_index)
        w = self.c.frame.body
        for tag in self.tags:
            w.tag_remove(tag,self.index(0),self.index("end")) # 10/27/03

        for tag in self.color_tags_list:
            w.tag_remove(tag,self.index(0),self.index("end")) # 10/27/03
    #@-node:ekr.20031218072017.1604:removeAllTags & removeTagsFromLines
    #@-node:ekr.20031218072017.1892:colorizeLine & allies
    #@+node:ekr.20050420083821:disable & enable
    def disable (self):

        # g.pr("disabling all syntax coloring")
        self.enabled=False

    def enable (self):

        self.enabled=True
    #@-node:ekr.20050420083821:disable & enable
    #@+node:ekr.20031218072017.2803:getCwebWord
    def getCwebWord (self,s,i):

        # g.trace(g.get_line(s,i))
        if not g.match(s,i,"@"):
            return None

        ch1 = ch2 = word = None
        if i + 1 < len(s): ch1 = s[i+1]
        if i + 2 < len(s): ch2 = s[i+2]

        if g.match(s,i,"@**"):
            word = "@**"
        elif not ch1:
            word = "@"
        elif not ch2:
            word = s[i:i+2]
        elif (
            (ch1 in string.ascii_letters and not ch2 in string.ascii_letters) or # single-letter control code
            ch1 not in string.ascii_letters # non-letter control code
        ):
            word = s[i:i+2]

        # if word: g.trace(word)

        return word
    #@-node:ekr.20031218072017.2803:getCwebWord
    #@+node:ekr.20071009094150:isSameColorState
    def isSameColorState (self):

        return False
    #@-node:ekr.20071009094150:isSameColorState
    #@+node:ekr.20031218072017.1944:removeAllImages (leoColor)
    def removeAllImages (self):

        '''Remove all references to previous images.
        In Tk, this will cause all images to disappear.'''

        self.image_references = []
    #@-node:ekr.20031218072017.1944:removeAllImages (leoColor)
    #@+node:ekr.20080828103146.8:scanColorDirectives (leoColor)
    def scanColorDirectives(self,p):

        '''Scan position p and p's ancestors looking for @comment, @language and @root directives,
        setting corresponding colorizer ivars.'''

        c = self.c
        if not c: return # May be None for testing.

        table = (
            ('lang-dict',   g.scanAtCommentAndAtLanguageDirectives),
            ('root',        c.scanAtRootDirectives),
        )

        # Set d by scanning all directives.
        aList = g.get_directives_dict_list(p)
        d = {}
        for key,func in table:
            val = func(aList)
            if val: d[key]=val

        # Post process.
        lang_dict       = d.get('lang-dict')
        self.rootMode   = d.get('root') or None

        if lang_dict:
            self.language       = lang_dict.get('language')
            self.comment_string = lang_dict.get('comment')
        else:
            self.language       = c.target_language and c.target_language.lower()
            self.comment_string = None

        # g.trace('self.language',self.language)
        return self.language # For use by external routines.
    #@-node:ekr.20080828103146.8:scanColorDirectives (leoColor)
    #@+node:ekr.20041217041016:setFontFromConfig (colorizer)
    def setFontFromConfig (self):

        c = self.c

        self.bold_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        if self.bold_font:
            self.bold_font.configure(weight="bold")

        self.italic_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        if self.italic_font:
            self.italic_font.configure(slant="italic",weight="normal")

        self.bolditalic_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant",  "body_text_font_weight",
            c.config.defaultBodyFontSize)

        if self.bolditalic_font:
            self.bolditalic_font.configure(weight="bold",slant="italic")

        self.color_tags_list = []
        self.image_references = []
    #@-node:ekr.20041217041016:setFontFromConfig (colorizer)
    #@+node:ekr.20031218072017.2804:updateSyntaxColorer
    # self.flag is True unless an unambiguous @nocolor is seen.

    def updateSyntaxColorer (self,p):

        p = p.copy()
        self.flag = self.useSyntaxColoring(p)
        self.scanColorDirectives(p)
    #@-node:ekr.20031218072017.2804:updateSyntaxColorer
    #@+node:ekr.20031218072017.2805:useSyntaxColoring
    def useSyntaxColoring (self,p):

        """Return True unless p is unambiguously under the control of @nocolor."""

        p = p.copy() ; first = p.copy()
        self.killFlag = False

        # New in Leo 4.6: @nocolor-node disables one node only.
        theDict = g.get_directives_dict(p)
        if 'nocolor-node' in theDict:
            return False

        for p in p.self_and_parents():
            theDict = g.get_directives_dict(p)
            no_color = 'nocolor' in theDict
            color = 'color' in theDict
            kill_color = 'killcolor' in theDict
            # A killcolor anywhere disables coloring.
            if kill_color:
                self.killFlag = True
                return False
            # A color anywhere in the target enables coloring.
            elif color and p == first:
                return True
            # Otherwise, the @nocolor specification must be unambiguous.
            elif no_color and not color:
                return False
            elif color and not no_color:
                return True

        return True
    #@-node:ekr.20031218072017.2805:useSyntaxColoring
    #@+node:ekr.20031218072017.2806:Utils
    #@+at 
    #@nonl
    # These methods are like the corresponding functions in 
    # leoGlobals.py except they issue no error messages.
    #@-at
    #@+node:ekr.20031218072017.1609:index & tag (leoColor)
    def index (self,i):

        # Short-circuit the redundant computations.
        w = self.c.frame.body.bodyCtrl ; s = self.allBodyText
        return w.rowColToGuiIndex(s,self.line_index-1,i)

    def tag (self,name,i,j):

        self.c.frame.body.tag_add(name,self.index(i),self.index(j))
    #@-node:ekr.20031218072017.1609:index & tag (leoColor)
    #@+node:ekr.20031218072017.2807:setFirstLineState
    def setFirstLineState (self):

        if self.flag:
            if self.rootMode:
                state = g.choose(self.rootMode=="code","normal","doc")
            else:
                state = "normal"
        else:
            state = "nocolor"

        return state
    #@-node:ekr.20031218072017.2807:setFirstLineState
    #@+node:ekr.20031218072017.2808:skip_id
    def skip_id(self,s,i,chars=None):

        n = len(s)

        # if not g.isPython3:
            # chars = chars and g.toUnicode(chars,encoding='ascii') or unicode('')

        chars = chars or g.u('')

        while i < n and (g.isWordChar(s[i]) or s[i] in chars):
                i += 1
        return i
    #@-node:ekr.20031218072017.2808:skip_id
    #@+node:ekr.20031218072017.1610:skip_python_string
    def skip_python_string(self,s,i):

        delim = s[i:i+3]
        if delim == "'''" or delim == '"""':
            k = s.find(delim,i+3)
            if k == -1:
                return len(s),g.choose(delim=="'''","string3s","string3d")
            else:
                return k+3, "normal"
        else:
            return self.skip_string(s,i)
    #@-node:ekr.20031218072017.1610:skip_python_string
    #@+node:ekr.20031218072017.2809:skip_string
    def skip_string(self,s,i):

        """Skip a string literal."""

        allow_newlines = self.language == "elisp"
        delim = s[i] ; i += 1
        continue_state = g.choose(delim=="'","singleString","doubleString")
        assert(delim == '"' or delim == "'")
        n = len(s)
        while i < n and s[i] != delim and (allow_newlines or not s[i] == '\n'): # 6/3/04: newline ends most strings.
            if s[i:] == "\\": # virtual trailing newline.
                return n,continue_state
            elif s[i] == '\\': i += 2
            else: i += 1

        if i >= n:
            return n, g.choose(allow_newlines,continue_state,"normal")
        if s[i] == delim:
            i += 1
        return i,"normal"
    #@-node:ekr.20031218072017.2809:skip_string
    #@-node:ekr.20031218072017.2806:Utils
    #@-others
#@-node:ekr.20031218072017.2796:class colorizer
#@+node:ekr.20031218072017.2218:class nullColorizer
class nullColorizer (colorizer):

    """A do-nothing colorer class"""

    #@    @+others
    #@+node:ekr.20031218072017.2219:__init__
    def __init__ (self,c):

        colorizer.__init__(self,c) # init the base class.

        self.c = c
        self.enabled = False
    #@-node:ekr.20031218072017.2219:__init__
    #@+node:ekr.20031218072017.2220:entry points
    def colorize(self,p,incremental=False,interruptable=True):
        return 'ok' # Used by unit tests.

    def disable(self):                          pass
    def enable(self):                           pass
    def scanColorDirectives(self,p):            pass

    def setFontFromConfig (self):
        self.bold_font = None
        self.italic_font = None
        self.bolditalic_font = None
        self.color_tags_list = []
        self.image_references = []

    def updateSyntaxColorer (self,p):           pass

    #@-node:ekr.20031218072017.2220:entry points
    #@-others
#@-node:ekr.20031218072017.2218:class nullColorizer
#@-others
#@-node:ekr.20031218072017.2794:@thin leoColor.py
#@-leo
