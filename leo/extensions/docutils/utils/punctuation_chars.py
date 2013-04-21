# !/usr/bin/env python
# -*- coding: utf8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20130421002947.10744: * @file C:\leo.repo\trunk\leo\extensions\docutils\utils\punctuation_chars.py
#@@first
#@@first
#@@language python
#@@tabwidth -4
# :Copyright: © 2011 Günter Milde.
# :License: Released under the terms of the `2-Clause BSD license`_, in short:
#
#    Copying and distribution of this file, with or without modification,
#    are permitted in any medium without royalty provided the copyright
#    notice and this notice are preserved.
#    This file is offered as-is, without any warranty.
#
# .. _2-Clause BSD license: http://www.spdx.org/licenses/BSD-2-Clause

# :Id: $Id: punctuation_chars.py 7463 2012-06-22 19:49:51Z milde $

#@+others
#@+node:ekr.20130421002947.10749: ** define_closers
# closers = ur"""\"\'\)\>\]\}༻༽᚜⁆⁾₎〉❩❫❭❯❱❳❵⟆⟧⟩⟫⟭⟯⦄⦆⦈⦊⦌⦎⦐⦒⦔⦖⦘⧙⧛⧽⸣⸥⸧⸩〉》」』】〕〗〙〛〞〟﴿︘︶︸︺︼︾﹀﹂﹄﹈﹚﹜﹞）］｝｠｣»’”›⸃⸅⸊⸍⸝⸡‛‟«‘“‹⸂⸄⸉⸌⸜⸠‚„"""

def define_closers():
    
    closers_list = [
       34, # QUOTATION MARK
       39, # APOSTROPHE
       41, # RIGHT PARENTHESIS
       62, # GREATER-THAN SIGN
       92, # REVERSE SOLIDUS
       93, # RIGHT SQUARE BRACKET
      125, # RIGHT CURLY BRACKET
      171, # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
      187, # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
     3899, # TIBETAN MARK GUG RTAGS GYAS
     3901, # TIBETAN MARK ANG KHANG GYAS
     5788, # OGHAM REVERSED FEATHER MARK
     8216, # LEFT SINGLE QUOTATION MARK
     8217, # RIGHT SINGLE QUOTATION MARK
     8218, # SINGLE LOW-9 QUOTATION MARK
     8219, # SINGLE HIGH-REVERSED-9 QUOTATION MARK
     8220, # LEFT DOUBLE QUOTATION MARK
     8221, # RIGHT DOUBLE QUOTATION MARK
     8222, # DOUBLE LOW-9 QUOTATION MARK
     8223, # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
     8249, # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
     8250, # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
     8262, # RIGHT SQUARE BRACKET WITH QUILL
     8318, # SUPERSCRIPT RIGHT PARENTHESIS
     8334, # SUBSCRIPT RIGHT PARENTHESIS
     9002, # RIGHT-POINTING ANGLE BRACKET
    10089, # MEDIUM RIGHT PARENTHESIS ORNAMENT
    10091, # MEDIUM FLATTENED RIGHT PARENTHESIS ORNAMENT
    10093, # MEDIUM RIGHT-POINTING ANGLE BRACKET ORNAMENT
    10095, # HEAVY RIGHT-POINTING ANGLE QUOTATION MARK ORNAMENT
    10097, # HEAVY RIGHT-POINTING ANGLE BRACKET ORNAMENT
    10099, # LIGHT RIGHT TORTOISE SHELL BRACKET ORNAMENT
    10101, # MEDIUM RIGHT CURLY BRACKET ORNAMENT
    10182, # RIGHT S-SHAPED BAG DELIMITER
    10215, # MATHEMATICAL RIGHT WHITE SQUARE BRACKET
    10217, # MATHEMATICAL RIGHT ANGLE BRACKET
    10219, # MATHEMATICAL RIGHT DOUBLE ANGLE BRACKET
    10221, # MATHEMATICAL RIGHT WHITE TORTOISE SHELL BRACKET
    10223, # MATHEMATICAL RIGHT FLATTENED PARENTHESIS
    10628, # RIGHT WHITE CURLY BRACKET
    10630, # RIGHT WHITE PARENTHESIS
    10632, # Z NOTATION RIGHT IMAGE BRACKET
    10634, # Z NOTATION RIGHT BINDING BRACKET
    10636, # RIGHT SQUARE BRACKET WITH UNDERBAR
    10638, # RIGHT SQUARE BRACKET WITH TICK IN BOTTOM CORNER
    10640, # RIGHT SQUARE BRACKET WITH TICK IN TOP CORNER
    10642, # RIGHT ANGLE BRACKET WITH DOT
    10644, # RIGHT ARC GREATER-THAN BRACKET
    10646, # DOUBLE RIGHT ARC LESS-THAN BRACKET
    10648, # RIGHT BLACK TORTOISE SHELL BRACKET
    10713, # RIGHT WIGGLY FENCE
    10715, # RIGHT DOUBLE WIGGLY FENCE
    10749, # RIGHT-POINTING CURVED ANGLE BRACKET
    11778, # LEFT SUBSTITUTION BRACKET
    11779, # RIGHT SUBSTITUTION BRACKET
    11780, # LEFT DOTTED SUBSTITUTION BRACKET
    11781, # RIGHT DOTTED SUBSTITUTION BRACKET
    11785, # LEFT TRANSPOSITION BRACKET
    11786, # RIGHT TRANSPOSITION BRACKET
    11788, # LEFT RAISED OMISSION BRACKET
    11789, # RIGHT RAISED OMISSION BRACKET
    11804, # LEFT LOW PARAPHRASE BRACKET
    11805, # RIGHT LOW PARAPHRASE BRACKET
    11808, # LEFT VERTICAL BAR WITH QUILL
    11809, # RIGHT VERTICAL BAR WITH QUILL
    11811, # TOP RIGHT HALF BRACKET
    11813, # BOTTOM RIGHT HALF BRACKET
    11815, # RIGHT SIDEWAYS U BRACKET
    11817, # RIGHT DOUBLE PARENTHESIS
    12297, # RIGHT ANGLE BRACKET
    12299, # RIGHT DOUBLE ANGLE BRACKET
    12301, # RIGHT CORNER BRACKET
    12303, # RIGHT WHITE CORNER BRACKET
    12305, # RIGHT BLACK LENTICULAR BRACKET
    12309, # RIGHT TORTOISE SHELL BRACKET
    12311, # RIGHT WHITE LENTICULAR BRACKET
    12313, # RIGHT WHITE TORTOISE SHELL BRACKET
    12315, # RIGHT WHITE SQUARE BRACKET
    12318, # DOUBLE PRIME QUOTATION MARK
    12319, # LOW DOUBLE PRIME QUOTATION MARK
    64831, # ORNATE RIGHT PARENTHESIS
    65048, # PRESENTATION FORM FOR VERTICAL RIGHT WHITE LENTICULAR BRAKCET
    65078, # PRESENTATION FORM FOR VERTICAL RIGHT PARENTHESIS
    65080, # PRESENTATION FORM FOR VERTICAL RIGHT CURLY BRACKET
    65082, # PRESENTATION FORM FOR VERTICAL RIGHT TORTOISE SHELL BRACKET
    65084, # PRESENTATION FORM FOR VERTICAL RIGHT BLACK LENTICULAR BRACKET
    65086, # PRESENTATION FORM FOR VERTICAL RIGHT DOUBLE ANGLE BRACKET
    65088, # PRESENTATION FORM FOR VERTICAL RIGHT ANGLE BRACKET
    65090, # PRESENTATION FORM FOR VERTICAL RIGHT CORNER BRACKET
    65092, # PRESENTATION FORM FOR VERTICAL RIGHT WHITE CORNER BRACKET
    65096, # PRESENTATION FORM FOR VERTICAL RIGHT SQUARE BRACKET
    65114, # SMALL RIGHT PARENTHESIS
    65116, # SMALL RIGHT CURLY BRACKET
    65118, # SMALL RIGHT TORTOISE SHELL BRACKET
    65289, # FULLWIDTH RIGHT PARENTHESIS
    65341, # FULLWIDTH RIGHT SQUARE BRACKET
    65373, # FULLWIDTH RIGHT CURLY BRACKET
    65376, # FULLWIDTH RIGHT WHITE PARENTHESIS
    65379, # HALFWIDTH RIGHT CORNER BRACKET
    
    ]
    return ''.join([ch(i) for i in closers_list])
#@+node:ekr.20130421002947.10751: ** define_closing_delimiters
def define_closing_delimiters():
    
    aList = [
    33, # EXCLAMATION MARK
    44, # COMMA
    46, # FULL STOP
    59, # SEMICOLON
    63, # QUESTION MARK
    92, # REVERSE SOLIDUS
    ]
    return ''.join([ch(i) for i in aList])
#@+node:ekr.20130421002947.10745: ** define_delimiters
### delimiters = ur"\-\/\:֊־᐀᠆‐‑‒–—―⸗⸚〜〰゠︱︲﹘﹣－¡·¿;·՚՛՜՝՞՟։׀׃׆׳״؉؊،؍؛؞؟٪٫٬٭۔܀܁܂܃܄܅܆܇܈܉܊܋܌܍߷߸߹࠰࠱࠲࠳࠴࠵࠶࠷࠸࠹࠺࠻࠼࠽࠾।॥॰෴๏๚๛༄༅༆༇༈༉༊་༌།༎༏༐༑༒྅࿐࿑࿒࿓࿔၊။၌၍၎၏჻፡።፣፤፥፦፧፨᙭᙮᛫᛬᛭᜵᜶។៕៖៘៙៚᠀᠁᠂᠃᠄᠅᠇᠈᠉᠊᥄᥅᧞᧟᨞᨟᪠᪡᪢᪣᪤᪥᪦᪨᪩᪪᪫᪬᪭᭚᭛᭜᭝᭞᭟᭠᰻᰼᰽᰾᰿᱾᱿᳓‖‗†‡•‣․‥…‧‰‱′″‴‵‶‷‸※‼‽‾⁁⁂⁃⁇⁈⁉⁊⁋⁌⁍⁎⁏⁐⁑⁓⁕⁖⁗⁘⁙⁚⁛⁜⁝⁞⳹⳺⳻⳼⳾⳿⸀⸁⸆⸇⸈⸋⸎⸏⸐⸑⸒⸓⸔⸕⸖⸘⸙⸛⸞⸟⸪⸫⸬⸭⸮⸰⸱、。〃〽・꓾꓿꘍꘎꘏꙳꙾꛲꛳꛴꛵꛶꛷꡴꡵꡶꡷꣎꣏꣸꣹꣺꤮꤯꥟꧁꧂꧃꧄꧅꧆꧇꧈꧉꧊꧋꧌꧍꧞꧟꩜꩝꩞꩟꫞꫟꯫︐︑︒︓︔︕︖︙︰﹅﹆﹉﹊﹋﹌﹐﹑﹒﹔﹕﹖﹗﹟﹠﹡﹨﹪﹫！＂＃％＆＇＊，．／：；？＠＼｡､･𐄀𐄁𐎟𐏐𐡗𐤟𐤿𐩐𐩑𐩒𐩓𐩔𐩕𐩖𐩗𐩘𐩿𐬹𐬺𐬻𐬼𐬽𐬾𐬿𑂻𑂼𑂾𑂿𑃀𑃁𒑰𒑱𒑲𒑳"

def define_delimiters():
    
    delim_list = [
    45, # hyphen-minus
    47, # solidus
    58, # colon
    92, # reverse solidus
    161, # inverted exclamation mark
    183, # middle dot
    191, # inverted question mark
    894, # greek question mark
    903, # greek ano teleia
    1370, # armenian apostrophe
    1371, # armenian emphasis mark
    1372, # armenian exclamation mark
    1373, # armenian comma
    1374, # armenian question mark
    1375, # armenian abbreviation mark
    1417, # armenian full stop
    1418, # armenian hyphen
    1470, # hebrew punctuation maqaf
    1472, # hebrew punctuation paseq
    1475, # hebrew punctuation sof pasuq
    1478, # hebrew punctuation nun hafukha
    1523, # hebrew punctuation geresh
    1524, # hebrew punctuation gershayim
    1545, # arabic-indic per mille sign
    1546, # arabic-indic per ten thousand sign
    1548, # arabic comma
    1549, # arabic date separator
    1563, # arabic semicolon
    1566, # arabic triple dot punctuation mark
    1567, # arabic question mark
    1642, # arabic percent sign
    1643, # arabic decimal separator
    1644, # arabic thousands separator
    1645, # arabic five pointed star
    1748, # arabic full stop
    1792, # syriac end of paragraph
    1793, # syriac supralinear full stop
    1794, # syriac sublinear full stop
    1795, # syriac supralinear colon
    1796, # syriac sublinear colon
    1797, # syriac horizontal colon
    1798, # syriac colon skewed left
    1799, # syriac colon skewed right
    1800, # syriac supralinear colon skewed left
    1801, # syriac sublinear colon skewed right
    1802, # syriac contraction
    1803, # syriac harklean obelus
    1804, # syriac harklean metobelus
    1805, # syriac harklean asteriscus
    2039, # nko symbol gbakurunen
    2040, # nko comma
    2041, # nko exclamation mark
    2096, # samaritan punctuation nequdaa
    2097, # samaritan punctuation afsaaq
    2098, # samaritan punctuation anged
    2099, # samaritan punctuation bau
    2100, # samaritan punctuation atmaau
    2101, # samaritan punctuation shiyyaalaa
    2102, # samaritan abbreviation mark
    2103, # samaritan punctuation melodic qitsa
    2104, # samaritan punctuation ziqaa
    2105, # samaritan punctuation qitsa
    2106, # samaritan punctuation zaef
    2107, # samaritan punctuation turu
    2108, # samaritan punctuation arkaanu
    2109, # samaritan punctuation sof mashfaat
    2110, # samaritan punctuation annaau
    2404, # devanagari danda
    2405, # devanagari double danda
    2416, # devanagari abbreviation sign
    3572, # sinhala punctuation kunddaliya
    3663, # thai character fongman
    3674, # thai character angkhankhu
    3675, # thai character khomut
    3844, # tibetan mark initial yig mgo mdun ma
    3845, # tibetan mark closing yig mgo sgab ma
    3846, # tibetan mark caret yig mgo phur shad ma
    3847, # tibetan mark yig mgo tsheg shad ma
    3848, # tibetan mark sbrul shad
    3849, # tibetan mark bskur yig mgo
    3850, # tibetan mark bka- shog yig mgo
    3851, # tibetan mark intersyllabic tsheg
    3852, # tibetan mark delimiter tsheg bstar
    3853, # tibetan mark shad
    3854, # tibetan mark nyis shad
    3855, # tibetan mark tsheg shad
    3856, # tibetan mark nyis tsheg shad
    3857, # tibetan mark rin chen spungs shad
    3858, # tibetan mark rgya gram shad
    3973, # tibetan mark paluta
    4048, # tibetan mark bska- shog gi mgo rgyan
    4049, # tibetan mark mnyam yig gi mgo rgyan
    4050, # tibetan mark nyis tsheg
    4051, # tibetan mark initial brda rnying yig mgo mdun ma
    4052, # tibetan mark closing brda rnying yig mgo sgab ma
    4170, # myanmar sign little section
    4171, # myanmar sign section
    4172, # myanmar symbol locative
    4173, # myanmar symbol completed
    4174, # myanmar symbol aforementioned
    4175, # myanmar symbol genitive
    4347, # georgian paragraph separator
    4961, # ethiopic wordspace
    4962, # ethiopic full stop
    4963, # ethiopic comma
    4964, # ethiopic semicolon
    4965, # ethiopic colon
    4966, # ethiopic preface colon
    4967, # ethiopic question mark
    4968, # ethiopic paragraph separator
    5120, # canadian syllabics hyphen
    5741, # canadian syllabics chi sign
    5742, # canadian syllabics full stop
    5867, # runic single punctuation
    5868, # runic multiple punctuation
    5869, # runic cross punctuation
    5941, # philippine single punctuation
    5942, # philippine double punctuation
    6100, # khmer sign khan
    6101, # khmer sign bariyoosan
    6102, # khmer sign camnuc pii kuuh
    6104, # khmer sign beyyal
    6105, # khmer sign phnaek muan
    6106, # khmer sign koomuut
    6144, # mongolian birga
    6145, # mongolian ellipsis
    6146, # mongolian comma
    6147, # mongolian full stop
    6148, # mongolian colon
    6149, # mongolian four dots
    6150, # mongolian todo soft hyphen
    6151, # mongolian sibe syllable boundary marker
    6152, # mongolian manchu comma
    6153, # mongolian manchu full stop
    6154, # mongolian nirugu
    6468, # limbu exclamation mark
    6469, # limbu question mark
    6622, # new tai lue sign lae
    6623, # new tai lue sign laev
    6686, # buginese pallawa
    6687, # buginese end of section
    6816, # tai tham sign wiang
    6817, # tai tham sign wiangwaak
    6818, # tai tham sign sawan
    6819, # tai tham sign keow
    6820, # tai tham sign hoy
    6821, # tai tham sign dokmai
    6822, # tai tham sign reversed rotated rana
    6824, # tai tham sign kaan
    6825, # tai tham sign kaankuu
    6826, # tai tham sign satkaan
    6827, # tai tham sign satkaankuu
    6828, # tai tham sign hang
    6829, # tai tham sign caang
    7002, # balinese panti
    7003, # balinese pamada
    7004, # balinese windu
    7005, # balinese carik pamungkah
    7006, # balinese carik siki
    7007, # balinese carik pareren
    7008, # balinese pameneng
    7227, # lepcha punctuation ta-rol
    7228, # lepcha punctuation nyet thyoom ta-rol
    7229, # lepcha punctuation cer-wa
    7230, # lepcha punctuation tshook cer-wa
    7231, # lepcha punctuation tshook
    7294, # ol chiki punctuation mucaad
    7295, # ol chiki punctuation double mucaad
    7379, # vedic sign nihshvasa
    8208, # hyphen
    8209, # non-breaking hyphen
    8210, # figure dash
    8211, # en dash
    8212, # em dash
    8213, # horizontal bar
    8214, # double vertical line
    8215, # double low line
    8224, # dagger
    8225, # double dagger
    8226, # bullet
    8227, # triangular bullet
    8228, # one dot leader
    8229, # two dot leader
    8230, # horizontal ellipsis
    8231, # hyphenation point
    8240, # per mille sign
    8241, # per ten thousand sign
    8242, # prime
    8243, # double prime
    8244, # triple prime
    8245, # reversed prime
    8246, # reversed double prime
    8247, # reversed triple prime
    8248, # caret
    8251, # reference mark
    8252, # double exclamation mark
    8253, # interrobang
    8254, # overline
    8257, # caret insertion point
    8258, # asterism
    8259, # hyphen bullet
    8263, # double question mark
    8264, # question exclamation mark
    8265, # exclamation question mark
    8266, # tironian sign et
    8267, # reversed pilcrow sign
    8268, # black leftwards bullet
    8269, # black rightwards bullet
    8270, # low asterisk
    8271, # reversed semicolon
    8272, # close up
    8273, # two asterisks aligned vertically
    8275, # swung dash
    8277, # flower punctuation mark
    8278, # three dot punctuation
    8279, # quadruple prime
    8280, # four dot punctuation
    8281, # five dot punctuation
    8282, # two dot punctuation
    8283, # four dot mark
    8284, # dotted cross
    8285, # tricolon
    8286, # vertical four dots
    11513, # coptic old nubian full stop
    11514, # coptic old nubian direct question mark
    11515, # coptic old nubian indirect question mark
    11516, # coptic old nubian verse divider
    11518, # coptic full stop
    11519, # coptic morphological divider
    11776, # right angle substitution marker
    11777, # right angle dotted substitution marker
    11782, # raised interpolation marker
    11783, # raised dotted interpolation marker
    11784, # dotted transposition marker
    11787, # raised square
    11790, # editorial coronis
    11791, # paragraphos
    11792, # forked paragraphos
    11793, # reversed forked paragraphos
    11794, # hypodiastole
    11795, # dotted obelos
    11796, # downwards ancora
    11797, # upwards ancora
    11798, # dotted right-pointing angle
    11799, # double oblique hyphen
    11800, # inverted interrobang
    11801, # palm branch
    11802, # hyphen with diaeresis
    11803, # tilde with ring above
    11806, # tilde with dot above
    11807, # tilde with dot below
    11818, # two dots over one dot punctuation
    11819, # one dot over two dots punctuation
    11820, # squared four dot punctuation
    11821, # five dot mark
    11822, # reversed question mark
    11824, # ring point
    11825, # word separator middle dot
    12289, # ideographic comma
    12290, # ideographic full stop
    12291, # ditto mark
    12316, # wave dash
    12336, # wavy dash
    12349, # part alternation mark
    12448, # katakana-hiragana double hyphen
    12539, # katakana middle dot
    42238, # lisu punctuation comma
    42239, # lisu punctuation full stop
    42509, # vai comma
    42510, # vai full stop
    42511, # vai question mark
    42611, # slavonic asterisk
    42622, # cyrillic kavyka
    42738, # bamum njaemli
    42739, # bamum full stop
    42740, # bamum colon
    42741, # bamum comma
    42742, # bamum semicolon
    42743, # bamum question mark
    43124, # phags-pa single head mark
    43125, # phags-pa double head mark
    43126, # phags-pa mark shad
    43127, # phags-pa mark double shad
    43214, # saurashtra danda
    43215, # saurashtra double danda
    43256, # devanagari sign pushpika
    43257, # devanagari gap filler
    43258, # devanagari caret
    43310, # kayah li sign cwi
    43311, # kayah li sign shya
    43359, # rejang section mark
    43457, # javanese left rerenggan
    43458, # javanese right rerenggan
    43459, # javanese pada andap
    43460, # javanese pada madya
    43461, # javanese pada luhur
    43462, # javanese pada windu
    43463, # javanese pada pangkat
    43464, # javanese pada lingsa
    43465, # javanese pada lungsi
    43466, # javanese pada adeg
    43467, # javanese pada adeg adeg
    43468, # javanese pada piseleh
    43469, # javanese turned pada piseleh
    43486, # javanese pada tirta tumetes
    43487, # javanese pada isen-isen
    43612, # cham punctuation spiral
    43613, # cham punctuation danda
    43614, # cham punctuation double danda
    43615, # cham punctuation triple danda
    43742, # tai viet symbol ho hoi
    43743, # tai viet symbol koi koi
    44011, # meetei mayek cheikhei
    65040, # presentation form for vertical comma
    65041, # presentation form for vertical ideographic comma
    65042, # presentation form for vertical ideographic full stop
    65043, # presentation form for vertical colon
    65044, # presentation form for vertical semicolon
    65045, # presentation form for vertical exclamation mark
    65046, # presentation form for vertical question mark
    65049, # presentation form for vertical horizontal ellipsis
    65072, # presentation form for vertical two dot leader
    65073, # presentation form for vertical em dash
    65074, # presentation form for vertical en dash
    65093, # sesame dot
    65094, # white sesame dot
    65097, # dashed overline
    65098, # centreline overline
    65099, # wavy overline
    65100, # double wavy overline
    65104, # small comma
    65105, # small ideographic comma
    65106, # small full stop
    65108, # small semicolon
    65109, # small colon
    65110, # small question mark
    65111, # small exclamation mark
    65112, # small em dash
    65119, # small number sign
    65120, # small ampersand
    65121, # small asterisk
    65123, # small hyphen-minus
    65128, # small reverse solidus
    65130, # small percent sign
    65131, # small commercial at
    65281, # fullwidth exclamation mark
    65282, # fullwidth quotation mark
    65283, # fullwidth number sign
    65285, # fullwidth percent sign
    65286, # fullwidth ampersand
    65287, # fullwidth apostrophe
    65290, # fullwidth asterisk
    65292, # fullwidth comma
    65293, # fullwidth hyphen-minus
    65294, # fullwidth full stop
    65295, # fullwidth solidus
    65306, # fullwidth colon
    65307, # fullwidth semicolon
    65311, # fullwidth question mark
    65312, # fullwidth commercial at
    65340, # fullwidth reverse solidus
    65377, # halfwidth ideographic full stop
    65380, # halfwidth ideographic comma
    65381, # halfwidth katakana middle dot
    ]
    return ''.join([ch(i) for i in delim_list])
    
#@+node:ekr.20130421002947.10746: ** define_openers
# openers = ur"""\"\'\(\<\[\{༺༼᚛⁅⁽₍〈❨❪❬❮❰❲❴⟅⟦⟨⟪⟬⟮⦃⦅⦇⦉⦋⦍⦏⦑⦓⦕⦗⧘⧚⧼⸢⸤⸦⸨〈《「『【〔〖〘〚〝〝﴾︗︵︷︹︻︽︿﹁﹃﹇﹙﹛﹝（［｛｟｢«‘“‹⸂⸄⸉⸌⸜⸠‚„»’”›⸃⸅⸊⸍⸝⸡‛‟"""

def define_openers():
    
    openers_list = [
       34, # QUOTATION MARK
       39, # APOSTROPHE
       40, # LEFT PARENTHESIS
       60, # LESS-THAN SIGN
       91, # LEFT SQUARE BRACKET
       92, # REVERSE SOLIDUS
      123, # LEFT CURLY BRACKET
      171, # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
      187, # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
     3898, # TIBETAN MARK GUG RTAGS GYON
     3900, # TIBETAN MARK ANG KHANG GYON
     5787, # OGHAM FEATHER MARK
     8216, # LEFT SINGLE QUOTATION MARK
     8217, # RIGHT SINGLE QUOTATION MARK
     8218, # SINGLE LOW-9 QUOTATION MARK
     8219, # SINGLE HIGH-REVERSED-9 QUOTATION MARK
     8220, # LEFT DOUBLE QUOTATION MARK
     8221, # RIGHT DOUBLE QUOTATION MARK
     8222, # DOUBLE LOW-9 QUOTATION MARK
     8223, # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
     8249, # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
     8250, # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
     8261, # LEFT SQUARE BRACKET WITH QUILL
     8317, # SUPERSCRIPT LEFT PARENTHESIS
     8333, # SUBSCRIPT LEFT PARENTHESIS
     9001, # LEFT-POINTING ANGLE BRACKET
    10088, # MEDIUM LEFT PARENTHESIS ORNAMENT
    10090, # MEDIUM FLATTENED LEFT PARENTHESIS ORNAMENT
    10092, # MEDIUM LEFT-POINTING ANGLE BRACKET ORNAMENT
    10094, # HEAVY LEFT-POINTING ANGLE QUOTATION MARK ORNAMENT
    10096, # HEAVY LEFT-POINTING ANGLE BRACKET ORNAMENT
    10098, # LIGHT LEFT TORTOISE SHELL BRACKET ORNAMENT
    10100, # MEDIUM LEFT CURLY BRACKET ORNAMENT
    10181, # LEFT S-SHAPED BAG DELIMITER
    10214, # MATHEMATICAL LEFT WHITE SQUARE BRACKET
    10216, # MATHEMATICAL LEFT ANGLE BRACKET
    10218, # MATHEMATICAL LEFT DOUBLE ANGLE BRACKET
    10220, # MATHEMATICAL LEFT WHITE TORTOISE SHELL BRACKET
    10222, # MATHEMATICAL LEFT FLATTENED PARENTHESIS
    10627, # LEFT WHITE CURLY BRACKET
    10629, # LEFT WHITE PARENTHESIS
    10631, # Z NOTATION LEFT IMAGE BRACKET
    10633, # Z NOTATION LEFT BINDING BRACKET
    10635, # LEFT SQUARE BRACKET WITH UNDERBAR
    10637, # LEFT SQUARE BRACKET WITH TICK IN TOP CORNER
    10639, # LEFT SQUARE BRACKET WITH TICK IN BOTTOM CORNER
    10641, # LEFT ANGLE BRACKET WITH DOT
    10643, # LEFT ARC LESS-THAN BRACKET
    10645, # DOUBLE LEFT ARC GREATER-THAN BRACKET
    10647, # LEFT BLACK TORTOISE SHELL BRACKET
    10712, # LEFT WIGGLY FENCE
    10714, # LEFT DOUBLE WIGGLY FENCE
    10748, # LEFT-POINTING CURVED ANGLE BRACKET
    11778, # LEFT SUBSTITUTION BRACKET
    11779, # RIGHT SUBSTITUTION BRACKET
    11780, # LEFT DOTTED SUBSTITUTION BRACKET
    11781, # RIGHT DOTTED SUBSTITUTION BRACKET
    11785, # LEFT TRANSPOSITION BRACKET
    11786, # RIGHT TRANSPOSITION BRACKET
    11788, # LEFT RAISED OMISSION BRACKET
    11789, # RIGHT RAISED OMISSION BRACKET
    11804, # LEFT LOW PARAPHRASE BRACKET
    11805, # RIGHT LOW PARAPHRASE BRACKET
    11808, # LEFT VERTICAL BAR WITH QUILL
    11809, # RIGHT VERTICAL BAR WITH QUILL
    11810, # TOP LEFT HALF BRACKET
    11812, # BOTTOM LEFT HALF BRACKET
    11814, # LEFT SIDEWAYS U BRACKET
    11816, # LEFT DOUBLE PARENTHESIS
    12296, # LEFT ANGLE BRACKET
    12298, # LEFT DOUBLE ANGLE BRACKET
    12300, # LEFT CORNER BRACKET
    12302, # LEFT WHITE CORNER BRACKET
    12304, # LEFT BLACK LENTICULAR BRACKET
    12308, # LEFT TORTOISE SHELL BRACKET
    12310, # LEFT WHITE LENTICULAR BRACKET
    12312, # LEFT WHITE TORTOISE SHELL BRACKET
    12314, # LEFT WHITE SQUARE BRACKET
    12317, # REVERSED DOUBLE PRIME QUOTATION MARK
    64830, # ORNATE LEFT PARENTHESIS
    65047, # PRESENTATION FORM FOR VERTICAL LEFT WHITE LENTICULAR BRACKET
    65077, # PRESENTATION FORM FOR VERTICAL LEFT PARENTHESIS
    65079, # PRESENTATION FORM FOR VERTICAL LEFT CURLY BRACKET
    65081, # PRESENTATION FORM FOR VERTICAL LEFT TORTOISE SHELL BRACKET
    65083, # PRESENTATION FORM FOR VERTICAL LEFT BLACK LENTICULAR BRACKET
    65085, # PRESENTATION FORM FOR VERTICAL LEFT DOUBLE ANGLE BRACKET
    65087, # PRESENTATION FORM FOR VERTICAL LEFT ANGLE BRACKET
    65089, # PRESENTATION FORM FOR VERTICAL LEFT CORNER BRACKET
    65091, # PRESENTATION FORM FOR VERTICAL LEFT WHITE CORNER BRACKET
    65095, # PRESENTATION FORM FOR VERTICAL LEFT SQUARE BRACKET
    65113, # SMALL LEFT PARENTHESIS
    65115, # SMALL LEFT CURLY BRACKET
    65117, # SMALL LEFT TORTOISE SHELL BRACKET
    65288, # FULLWIDTH LEFT PARENTHESIS
    65339, # FULLWIDTH LEFT SQUARE BRACKET
    65371, # FULLWIDTH LEFT CURLY BRACKET
    65375, # FULLWIDTH LEFT WHITE PARENTHESIS
    65378, # HALFWIDTH LEFT CORNER BRACKET
    ]
    return ''.join([ch(i) for i in openers_list])
#@-others

# punctuation characters around inline markup
# ===========================================
#
# This module provides the lists of characters for the implementation of
# the `inline markup recognition rules`_ in the reStructuredText parser
# (states.py)
#
# .. _inline markup recognition rules:
#     ../../../docs/ref/rst/restructuredtext.html#inline-markup

# Docutils punctuation category sample strings
# --------------------------------------------
#
# The sample strings are generated by punctuation_samples() and put here
# literal to avoid the time-consuming generation with every Docutils
# run. Running this file as a standalone module checks the definitions below
# against a re-calculation.

import sys
ch = unichr if sys.version_info < (3,) else chr

openers = define_openers()
closers = define_closers()
closing_delimiters = define_closing_delimiters()
delimiters = define_delimiters()

#@-leo
