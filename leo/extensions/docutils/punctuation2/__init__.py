#!/usr/bin/env python
# -*- coding: utf8 -*-
# punctuation2.py: Python 2.x syntax.
# This file by Edward K. Ream.

# :Copyright: © 2011 Günter Milde.
# :License: Released under the terms of the `2-Clause BSD license`_, in short:
#
#    Copying and distribution of this file, with or without modification,
#    are permitted in any medium without royalty provided the copyright
#    notice and this notice are preserved.
#    This file is offered as-is, without any warranty.
#
# .. _2-Clause BSD license: http://www.spdx.org/licenses/BSD-2-Clause

# fom punctuation_chars.py.

openers = ur"""\"\'\(\<\[\{༺༼᚛⁅⁽₍〈❨❪❬❮❰❲❴⟅⟦⟨⟪⟬⟮⦃⦅⦇⦉⦋⦍⦏⦑⦓⦕⦗⧘⧚⧼⸢⸤⸦⸨〈《「『【〔〖〘〚〝〝﴾︗︵︷︹︻︽︿﹁﹃﹇﹙﹛﹝（［｛｟｢«‘“‹⸂⸄⸉⸌⸜⸠‚„»’”›⸃⸅⸊⸍⸝⸡‛‟"""
closers = ur"""\"\'\)\>\]\}༻༽᚜⁆⁾₎〉❩❫❭❯❱❳❵⟆⟧⟩⟫⟭⟯⦄⦆⦈⦊⦌⦎⦐⦒⦔⦖⦘⧙⧛⧽⸣⸥⸧⸩〉》」』】〕〗〙〛〞〟﴿︘︶︸︺︼︾﹀﹂﹄﹈﹚﹜﹞）］｝｠｣»’”›⸃⸅⸊⸍⸝⸡‛‟«‘“‹⸂⸄⸉⸌⸜⸠‚„"""
delimiters = ur"\-\/\:֊־᐀᠆‐‑‒–—―⸗⸚〜〰゠︱︲﹘﹣－¡·¿;·՚՛՜՝՞՟։׀׃׆׳״؉؊،؍؛؞؟٪٫٬٭۔܀܁܂܃܄܅܆܇܈܉܊܋܌܍߷߸߹࠰࠱࠲࠳࠴࠵࠶࠷࠸࠹࠺࠻࠼࠽࠾।॥॰෴๏๚๛༄༅༆༇༈༉༊་༌།༎༏༐༑༒྅࿐࿑࿒࿓࿔၊။၌၍၎၏჻፡።፣፤፥፦፧፨᙭᙮᛫᛬᛭᜵᜶។៕៖៘៙៚᠀᠁᠂᠃᠄᠅᠇᠈᠉᠊᥄᥅᧞᧟᨞᨟᪠᪡᪢᪣᪤᪥᪦᪨᪩᪪᪫᪬᪭᭚᭛᭜᭝᭞᭟᭠᰻᰼᰽᰾᰿᱾᱿᳓‖‗†‡•‣․‥…‧‰‱′″‴‵‶‷‸※‼‽‾⁁⁂⁃⁇⁈⁉⁊⁋⁌⁍⁎⁏⁐⁑⁓⁕⁖⁗⁘⁙⁚⁛⁜⁝⁞⳹⳺⳻⳼⳾⳿⸀⸁⸆⸇⸈⸋⸎⸏⸐⸑⸒⸓⸔⸕⸖⸘⸙⸛⸞⸟⸪⸫⸬⸭⸮⸰⸱、。〃〽・꓾꓿꘍꘎꘏꙳꙾꛲꛳꛴꛵꛶꛷꡴꡵꡶꡷꣎꣏꣸꣹꣺꤮꤯꥟꧁꧂꧃꧄꧅꧆꧇꧈꧉꧊꧋꧌꧍꧞꧟꩜꩝꩞꩟꫞꫟꯫︐︑︒︓︔︕︖︙︰﹅﹆﹉﹊﹋﹌﹐﹑﹒﹔﹕﹖﹗﹟﹠﹡﹨﹪﹫！＂＃％＆＇＊，．／：；？＠＼｡､･𐄀𐄁𐎟𐏐𐡗𐤟𐤿𐩐𐩑𐩒𐩓𐩔𐩕𐩖𐩗𐩘𐩿𐬹𐬺𐬻𐬼𐬽𐬾𐬿𑂻𑂼𑂾𑂿𑃀𑃁𒑰𒑱𒑲𒑳"
closing_delimiters = ur"\.\,\;\!\?"

# From manpage.py.

replace_pairs = [
    (u'-', ur'\-'),
    (u'\'', ur'\(aq'),
    (u'´', ur'\''),
    (u'`', ur'\(ga'),
]

# From writers/latex2e/__init__.py

literal_double_quote = ur'\dq{}'
italian_literal_double_quote = ur'{\char`\"}'

table_reflectbox = ur'\reflectbox{/}'
table_textbar = ur'\textbar{}'
table_textless = ur'\textless{}'
table_textgreater = ur'\textgreater{}'
table_tilde = ur'~'

special_chars = {
    ord('#'): ur'\#',
    ord('%'): ur'\%',
    ord('\\'): ur'\\',
}

special = {
    ord('#'): ur'\#',
    ord('$'): ur'\$',
    ord('%'): ur'\%',
    ord('&'): ur'\&',
    ord('~'): ur'\textasciitilde{}',
    ord('_'): ur'\_',
    ord('^'): ur'\textasciicircum{}',
    ord('\\'): ur'\textbackslash{}',
    ord('{'): ur'\{',
    ord('}'): ur'\}',
    # Square brackets are ordinary chars and cannot be escaped with '\',
    # so we put them in a group '{[}'. (Alternative: ensure that all
    # macros with optional arguments are terminated with {} and text
    # inside any optional argument is put in a group ``[{text}]``).
    # Commands with optional args inside an optional arg must be put in a
    # group, e.g. ``\item[{\hyperref[label]{text}}]``.
    ord('['): ur'{[}',
    ord(']'): ur'{]}',
    # the soft hyphen is unknown in 8-bit text and not properly handled by XeTeX
    0x00AD: ur'\-', # SOFT HYPHEN
}

# Unicode chars that are not recognized by LaTeX's utf8 encoding
unsupported_unicode = {
    0x00A0: ur'~', # NO-BREAK SPACE
    # TODO: ensure white space also at the beginning of a line?
    # 0x00A0: ur'\leavevmode\nobreak\vadjust{}~'
    0x2008: ur'\,', # PUNCTUATION SPACE   
    0x2011: ur'\hbox{-}', # NON-BREAKING HYPHEN
    0x202F: ur'\,', # NARROW NO-BREAK SPACE
    0x21d4: ur'$\Leftrightarrow$',
    # Docutils footnote symbols:
    0x2660: ur'$\spadesuit$',
    0x2663: ur'$\clubsuit$',
}

# Unicode chars that are recognized by LaTeX's utf8 encoding
utf8_supported_unicode = {
    0x00AB: ur'\guillemotleft', # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    0x00bb: ur'\guillemotright', # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    0x200C: ur'\textcompwordmark', # ZERO WIDTH NON-JOINER
    0x2013: ur'\textendash{}',
    0x2014: ur'\textemdash{}',
    0x2018: ur'\textquoteleft{}',
    0x2019: ur'\textquoteright{}',
    0x201A: ur'\quotesinglbase{}', # SINGLE LOW-9 QUOTATION MARK
    0x201C: ur'\textquotedblleft{}',
    0x201D: ur'\textquotedblright{}',
    0x201E: ur'\quotedblbase{}', # DOUBLE LOW-9 QUOTATION MARK
    0x2030: ur'\textperthousand{}',   # PER MILLE SIGN
    0x2031: ur'\textpertenthousand{}', # PER TEN THOUSAND SIGN
    0x2039: ur'\guilsinglleft{}',
    0x203A: ur'\guilsinglright{}',
    0x2423: ur'\textvisiblespace{}',  # OPEN BOX
    0x2020: ur'\dag{}',
    0x2021: ur'\ddag{}',
    0x2026: ur'\dots{}',
    0x2122: ur'\texttrademark{}',
}

# recognized with 'utf8', if textcomp is loaded
textcomp = {
    # Latin-1 Supplement
    0x00a2: ur'\textcent{}',          # ¢ CENT SIGN
    0x00a4: ur'\textcurrency{}',      # ¤ CURRENCY SYMBOL
    0x00a5: ur'\textyen{}',           # ¥ YEN SIGN
    0x00a6: ur'\textbrokenbar{}',     # ¦ BROKEN BAR
    0x00a7: ur'\textsection{}',       # § SECTION SIGN
    0x00a8: ur'\textasciidieresis{}', # ¨ DIAERESIS
    0x00a9: ur'\textcopyright{}',     # © COPYRIGHT SIGN
    0x00aa: ur'\textordfeminine{}',   # ª FEMININE ORDINAL INDICATOR
    0x00ac: ur'\textlnot{}',          # ¬ NOT SIGN
    0x00ae: ur'\textregistered{}',    # ® REGISTERED SIGN
    0x00af: ur'\textasciimacron{}',   # ¯ MACRON
    0x00b0: ur'\textdegree{}',        # ° DEGREE SIGN
    0x00b1: ur'\textpm{}',            # ± PLUS-MINUS SIGN
    0x00b2: ur'\texttwosuperior{}',   # ² SUPERSCRIPT TWO
    0x00b3: ur'\textthreesuperior{}', # ³ SUPERSCRIPT THREE
    0x00b4: ur'\textasciiacute{}',    # ´ ACUTE ACCENT
    0x00b5: ur'\textmu{}',            # µ MICRO SIGN
    0x00b6: ur'\textparagraph{}',     # ¶ PILCROW SIGN # not equal to \textpilcrow
    0x00b9: ur'\textonesuperior{}',   # ¹ SUPERSCRIPT ONE
    0x00ba: ur'\textordmasculine{}',  # º MASCULINE ORDINAL INDICATOR
    0x00bc: ur'\textonequarter{}',    # 1/4 FRACTION
    0x00bd: ur'\textonehalf{}',       # 1/2 FRACTION
    0x00be: ur'\textthreequarters{}', # 3/4 FRACTION
    0x00d7: ur'\texttimes{}',         # × MULTIPLICATION SIGN
    0x00f7: ur'\textdiv{}',           # ÷ DIVISION SIGN
    #
    0x0192: ur'\textflorin{}',        # LATIN SMALL LETTER F WITH HOOK
    0x02b9: ur'\textasciiacute{}',    # MODIFIER LETTER PRIME
    0x02ba: ur'\textacutedbl{}',      # MODIFIER LETTER DOUBLE PRIME
    0x2016: ur'\textbardbl{}',        # DOUBLE VERTICAL LINE
    0x2022: ur'\textbullet{}',        # BULLET
    0x2032: ur'\textasciiacute{}',    # PRIME
    0x2033: ur'\textacutedbl{}',      # DOUBLE PRIME
    0x2035: ur'\textasciigrave{}',    # REVERSED PRIME
    0x2036: ur'\textgravedbl{}',      # REVERSED DOUBLE PRIME
    0x203b: ur'\textreferencemark{}', # REFERENCE MARK
    0x203d: ur'\textinterrobang{}',   # INTERROBANG
    0x2044: ur'\textfractionsolidus{}', # FRACTION SLASH
    0x2045: ur'\textlquill{}',        # LEFT SQUARE BRACKET WITH QUILL
    0x2046: ur'\textrquill{}',        # RIGHT SQUARE BRACKET WITH QUILL
    0x2052: ur'\textdiscount{}',      # COMMERCIAL MINUS SIGN
    0x20a1: ur'\textcolonmonetary{}', # COLON SIGN
    0x20a3: ur'\textfrenchfranc{}',   # FRENCH FRANC SIGN
    0x20a4: ur'\textlira{}',          # LIRA SIGN
    0x20a6: ur'\textnaira{}',         # NAIRA SIGN
    0x20a9: ur'\textwon{}',           # WON SIGN
    0x20ab: ur'\textdong{}',          # DONG SIGN
    0x20ac: ur'\texteuro{}',          # EURO SIGN
    0x20b1: ur'\textpeso{}',          # PESO SIGN
    0x20b2: ur'\textguarani{}',       # GUARANI SIGN
    0x2103: ur'\textcelsius{}',       # DEGREE CELSIUS
    0x2116: ur'\textnumero{}',        # NUMERO SIGN
    0x2117: ur'\textcircledP{}',      # SOUND RECORDING COYRIGHT
    0x211e: ur'\textrecipe{}',        # PRESCRIPTION TAKE
    0x2120: ur'\textservicemark{}',   # SERVICE MARK
    0x2122: ur'\texttrademark{}',     # TRADE MARK SIGN
    0x2126: ur'\textohm{}',           # OHM SIGN
    0x2127: ur'\textmho{}',           # INVERTED OHM SIGN
    0x212e: ur'\textestimated{}',     # ESTIMATED SYMBOL
    0x2190: ur'\textleftarrow{}',     # LEFTWARDS ARROW
    0x2191: ur'\textuparrow{}',       # UPWARDS ARROW
    0x2192: ur'\textrightarrow{}',    # RIGHTWARDS ARROW
    0x2193: ur'\textdownarrow{}',     # DOWNWARDS ARROW
    0x2212: ur'\textminus{}',         # MINUS SIGN
    0x2217: ur'\textasteriskcentered{}', # ASTERISK OPERATOR
    0x221a: ur'\textsurd{}',          # SQUARE ROOT
    0x2422: ur'\textblank{}',         # BLANK SYMBOL
    0x25e6: ur'\textopenbullet{}',    # WHITE BULLET
    0x25ef: ur'\textbigcircle{}',     # LARGE CIRCLE
    0x266a: ur'\textmusicalnote{}',   # EIGHTH NOTE
    0x26ad: ur'\textmarried{}',       # MARRIAGE SYMBOL
    0x26ae: ur'\textdivorced{}',      # DIVORCE SYMBOL
    0x27e8: ur'\textlangle{}',        # MATHEMATICAL LEFT ANGLE BRACKET
    0x27e9: ur'\textrangle{}',        # MATHEMATICAL RIGHT ANGLE BRACKET
}

# Unicode chars that require a feature/package to render
pifont = {
    0x2665: ur'\ding{170}',     # black heartsuit
    0x2666: ur'\ding{169}',     # black diamondsuit
    0x2713: ur'\ding{51}',      # check mark
    0x2717: ur'\ding{55}',      # check mark
}
