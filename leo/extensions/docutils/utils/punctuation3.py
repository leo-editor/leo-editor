#!/usr/bin/env python
# -*- coding: utf8 -*-
# punctuation3.py: Python 3.x syntax.
# This file by Edward K. Ream

# :Copyright: © 2011 Günter Milde.
# :License: Released under the terms of the `2-Clause BSD license`_, in short:
#
#    Copying and distribution of this file, with or without modification,
#    are permitted in any medium without royalty provided the copyright
#    notice and this notice are preserved.
#    This file is offered as-is, without any warranty.
#
# .. _2-Clause BSD license: http://www.spdx.org/licenses/BSD-2-Clause

# Extracted from punctuation_chars.py by Edward K. Ream.

openers = r"""\"\'\(\<\[\{༺༼᚛⁅⁽₍〈❨❪❬❮❰❲❴⟅⟦⟨⟪⟬⟮⦃⦅⦇⦉⦋⦍⦏⦑⦓⦕⦗⧘⧚⧼⸢⸤⸦⸨〈《「『【〔〖〘〚〝〝﴾︗︵︷︹︻︽︿﹁﹃﹇﹙﹛﹝（［｛｟｢«‘“‹⸂⸄⸉⸌⸜⸠‚„»’”›⸃⸅⸊⸍⸝⸡‛‟"""
closers = r"""\"\'\)\>\]\}༻༽᚜⁆⁾₎〉❩❫❭❯❱❳❵⟆⟧⟩⟫⟭⟯⦄⦆⦈⦊⦌⦎⦐⦒⦔⦖⦘⧙⧛⧽⸣⸥⸧⸩〉》」』】〕〗〙〛〞〟﴿︘︶︸︺︼︾﹀﹂﹄﹈﹚﹜﹞）］｝｠｣»’”›⸃⸅⸊⸍⸝⸡‛‟«‘“‹⸂⸄⸉⸌⸜⸠‚„"""
delimiters = r"\-\/\:֊־᐀᠆‐‑‒–—―⸗⸚〜〰゠︱︲﹘﹣－¡·¿;·՚՛՜՝՞՟։׀׃׆׳״؉؊،؍؛؞؟٪٫٬٭۔܀܁܂܃܄܅܆܇܈܉܊܋܌܍߷߸߹࠰࠱࠲࠳࠴࠵࠶࠷࠸࠹࠺࠻࠼࠽࠾।॥॰෴๏๚๛༄༅༆༇༈༉༊་༌།༎༏༐༑༒྅࿐࿑࿒࿓࿔၊။၌၍၎၏჻፡።፣፤፥፦፧፨᙭᙮᛫᛬᛭᜵᜶។៕៖៘៙៚᠀᠁᠂᠃᠄᠅᠇᠈᠉᠊᥄᥅᧞᧟᨞᨟᪠᪡᪢᪣᪤᪥᪦᪨᪩᪪᪫᪬᪭᭚᭛᭜᭝᭞᭟᭠᰻᰼᰽᰾᰿᱾᱿᳓‖‗†‡•‣․‥…‧‰‱′″‴‵‶‷‸※‼‽‾⁁⁂⁃⁇⁈⁉⁊⁋⁌⁍⁎⁏⁐⁑⁓⁕⁖⁗⁘⁙⁚⁛⁜⁝⁞⳹⳺⳻⳼⳾⳿⸀⸁⸆⸇⸈⸋⸎⸏⸐⸑⸒⸓⸔⸕⸖⸘⸙⸛⸞⸟⸪⸫⸬⸭⸮⸰⸱、。〃〽・꓾꓿꘍꘎꘏꙳꙾꛲꛳꛴꛵꛶꛷꡴꡵꡶꡷꣎꣏꣸꣹꣺꤮꤯꥟꧁꧂꧃꧄꧅꧆꧇꧈꧉꧊꧋꧌꧍꧞꧟꩜꩝꩞꩟꫞꫟꯫︐︑︒︓︔︕︖︙︰﹅﹆﹉﹊﹋﹌﹐﹑﹒﹔﹕﹖﹗﹟﹠﹡﹨﹪﹫！＂＃％＆＇＊，．／：；？＠＼｡､･𐄀𐄁𐎟𐏐𐡗𐤟𐤿𐩐𐩑𐩒𐩓𐩔𐩕𐩖𐩗𐩘𐩿𐬹𐬺𐬻𐬼𐬽𐬾𐬿𑂻𑂼𑂾𑂿𑃀𑃁𒑰𒑱𒑲𒑳"
closing_delimiters = r"\.\,\;\!\?"

# From manpage.py.

replace_pairs = [
    (u'-', ur'\-'),
    (u'\'', ur'\(aq'),
    (u'´', ur'\''),
    (u'`', ur'\(ga'),
]

# From writers/latex2e/__init__.py

literal_double_quote = r'\dq{}'
italian_literal_double_quote = r'{\char`\"}'

table_reflectbox = r'\reflectbox{/}'
table_textbar = r'\textbar{}'
table_textless = r'\textless{}'
table_textgreater = r'\textgreater{}'
table_tilde = r'~'

special_chars = {
    ord('#'): r'\#',
    ord('%'): r'\%',
    ord('\\'): r'\\',
}

special = {
    ord('#'): r'\#',
    ord('$'): r'\$',
    ord('%'): r'\%',
    ord('&'): r'\&',
    ord('~'): r'\textasciitilde{}',
    ord('_'): r'\_',
    ord('^'): r'\textasciicircum{}',
    ord('\\'): r'\textbackslash{}',
    ord('{'): r'\{',
    ord('}'): r'\}',
    # Square brackets are ordinary chars and cannot be escaped with '\',
    # so we put them in a group '{[}'. (Alternative: ensure that all
    # macros with optional arguments are terminated with {} and text
    # inside any optional argument is put in a group ``[{text}]``).
    # Commands with optional args inside an optional arg must be put in a
    # group, e.g. ``\item[{\hyperref[label]{text}}]``.
    ord('['): r'{[}',
    ord(']'): r'{]}',
    # the soft hyphen is unknown in 8-bit text and not properly handled by XeTeX
    0x00AD: r'\-', # SOFT HYPHEN
}

# Unicode chars that are not recognized by LaTeX's utf8 encoding
unsupported_unicode = {
    0x00A0: r'~', # NO-BREAK SPACE
    # TODO: ensure white space also at the beginning of a line?
    # 0x00A0: r'\leavevmode\nobreak\vadjust{}~'
    0x2008: r'\,', # PUNCTUATION SPACE   
    0x2011: r'\hbox{-}', # NON-BREAKING HYPHEN
    0x202F: r'\,', # NARROW NO-BREAK SPACE
    0x21d4: r'$\Leftrightarrow$',
    # Docutils footnote symbols:
    0x2660: r'$\spadesuit$',
    0x2663: r'$\clubsuit$',
}

# Unicode chars that are recognized by LaTeX's utf8 encoding
utf8_supported_unicode = {
    0x00AB: r'\guillemotleft', # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    0x00bb: r'\guillemotright', # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    0x200C: r'\textcompwordmark', # ZERO WIDTH NON-JOINER
    0x2013: r'\textendash{}',
    0x2014: r'\textemdash{}',
    0x2018: r'\textquoteleft{}',
    0x2019: r'\textquoteright{}',
    0x201A: r'\quotesinglbase{}', # SINGLE LOW-9 QUOTATION MARK
    0x201C: r'\textquotedblleft{}',
    0x201D: r'\textquotedblright{}',
    0x201E: r'\quotedblbase{}', # DOUBLE LOW-9 QUOTATION MARK
    0x2030: r'\textperthousand{}',   # PER MILLE SIGN
    0x2031: r'\textpertenthousand{}', # PER TEN THOUSAND SIGN
    0x2039: r'\guilsinglleft{}',
    0x203A: r'\guilsinglright{}',
    0x2423: r'\textvisiblespace{}',  # OPEN BOX
    0x2020: r'\dag{}',
    0x2021: r'\ddag{}',
    0x2026: r'\dots{}',
    0x2122: r'\texttrademark{}',
}

# recognized with 'utf8', if textcomp is loaded
textcomp = {
    # Latin-1 Supplement
    0x00a2: r'\textcent{}',          # ¢ CENT SIGN
    0x00a4: r'\textcurrency{}',      # ¤ CURRENCY SYMBOL
    0x00a5: r'\textyen{}',           # ¥ YEN SIGN
    0x00a6: r'\textbrokenbar{}',     # ¦ BROKEN BAR
    0x00a7: r'\textsection{}',       # § SECTION SIGN
    0x00a8: r'\textasciidieresis{}', # ¨ DIAERESIS
    0x00a9: r'\textcopyright{}',     # © COPYRIGHT SIGN
    0x00aa: r'\textordfeminine{}',   # ª FEMININE ORDINAL INDICATOR
    0x00ac: r'\textlnot{}',          # ¬ NOT SIGN
    0x00ae: r'\textregistered{}',    # ® REGISTERED SIGN
    0x00af: r'\textasciimacron{}',   # ¯ MACRON
    0x00b0: r'\textdegree{}',        # ° DEGREE SIGN
    0x00b1: r'\textpm{}',            # ± PLUS-MINUS SIGN
    0x00b2: r'\texttwosuperior{}',   # ² SUPERSCRIPT TWO
    0x00b3: r'\textthreesuperior{}', # ³ SUPERSCRIPT THREE
    0x00b4: r'\textasciiacute{}',    # ´ ACUTE ACCENT
    0x00b5: r'\textmu{}',            # µ MICRO SIGN
    0x00b6: r'\textparagraph{}',     # ¶ PILCROW SIGN # not equal to \textpilcrow
    0x00b9: r'\textonesuperior{}',   # ¹ SUPERSCRIPT ONE
    0x00ba: r'\textordmasculine{}',  # º MASCULINE ORDINAL INDICATOR
    0x00bc: r'\textonequarter{}',    # 1/4 FRACTION
    0x00bd: r'\textonehalf{}',       # 1/2 FRACTION
    0x00be: r'\textthreequarters{}', # 3/4 FRACTION
    0x00d7: r'\texttimes{}',         # × MULTIPLICATION SIGN
    0x00f7: r'\textdiv{}',           # ÷ DIVISION SIGN
    #
    0x0192: r'\textflorin{}',        # LATIN SMALL LETTER F WITH HOOK
    0x02b9: r'\textasciiacute{}',    # MODIFIER LETTER PRIME
    0x02ba: r'\textacutedbl{}',      # MODIFIER LETTER DOUBLE PRIME
    0x2016: r'\textbardbl{}',        # DOUBLE VERTICAL LINE
    0x2022: r'\textbullet{}',        # BULLET
    0x2032: r'\textasciiacute{}',    # PRIME
    0x2033: r'\textacutedbl{}',      # DOUBLE PRIME
    0x2035: r'\textasciigrave{}',    # REVERSED PRIME
    0x2036: r'\textgravedbl{}',      # REVERSED DOUBLE PRIME
    0x203b: r'\textreferencemark{}', # REFERENCE MARK
    0x203d: r'\textinterrobang{}',   # INTERROBANG
    0x2044: r'\textfractionsolidus{}', # FRACTION SLASH
    0x2045: r'\textlquill{}',        # LEFT SQUARE BRACKET WITH QUILL
    0x2046: r'\textrquill{}',        # RIGHT SQUARE BRACKET WITH QUILL
    0x2052: r'\textdiscount{}',      # COMMERCIAL MINUS SIGN
    0x20a1: r'\textcolonmonetary{}', # COLON SIGN
    0x20a3: r'\textfrenchfranc{}',   # FRENCH FRANC SIGN
    0x20a4: r'\textlira{}',          # LIRA SIGN
    0x20a6: r'\textnaira{}',         # NAIRA SIGN
    0x20a9: r'\textwon{}',           # WON SIGN
    0x20ab: r'\textdong{}',          # DONG SIGN
    0x20ac: r'\texteuro{}',          # EURO SIGN
    0x20b1: r'\textpeso{}',          # PESO SIGN
    0x20b2: r'\textguarani{}',       # GUARANI SIGN
    0x2103: r'\textcelsius{}',       # DEGREE CELSIUS
    0x2116: r'\textnumero{}',        # NUMERO SIGN
    0x2117: r'\textcircledP{}',      # SOUND RECORDING COYRIGHT
    0x211e: r'\textrecipe{}',        # PRESCRIPTION TAKE
    0x2120: r'\textservicemark{}',   # SERVICE MARK
    0x2122: r'\texttrademark{}',     # TRADE MARK SIGN
    0x2126: r'\textohm{}',           # OHM SIGN
    0x2127: r'\textmho{}',           # INVERTED OHM SIGN
    0x212e: r'\textestimated{}',     # ESTIMATED SYMBOL
    0x2190: r'\textleftarrow{}',     # LEFTWARDS ARROW
    0x2191: r'\textuparrow{}',       # UPWARDS ARROW
    0x2192: r'\textrightarrow{}',    # RIGHTWARDS ARROW
    0x2193: r'\textdownarrow{}',     # DOWNWARDS ARROW
    0x2212: r'\textminus{}',         # MINUS SIGN
    0x2217: r'\textasteriskcentered{}', # ASTERISK OPERATOR
    0x221a: r'\textsurd{}',          # SQUARE ROOT
    0x2422: r'\textblank{}',         # BLANK SYMBOL
    0x25e6: r'\textopenbullet{}',    # WHITE BULLET
    0x25ef: r'\textbigcircle{}',     # LARGE CIRCLE
    0x266a: r'\textmusicalnote{}',   # EIGHTH NOTE
    0x26ad: r'\textmarried{}',       # MARRIAGE SYMBOL
    0x26ae: r'\textdivorced{}',      # DIVORCE SYMBOL
    0x27e8: r'\textlangle{}',        # MATHEMATICAL LEFT ANGLE BRACKET
    0x27e9: r'\textrangle{}',        # MATHEMATICAL RIGHT ANGLE BRACKET
}

# Unicode chars that require a feature/package to render
pifont = {
    0x2665: r'\ding{170}',     # black heartsuit
    0x2666: r'\ding{169}',     # black diamondsuit
    0x2713: r'\ding{51}',      # check mark
    0x2717: r'\ding{55}',      # check mark
}
