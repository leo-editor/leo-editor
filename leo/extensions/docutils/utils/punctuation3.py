# -*- coding: utf8 -*-
# punctuation3.py: Python 3.x syntax.
# Extracted from punctuation_chars.py by Edward K. Ream.

# :Copyright: © 2011 Günter Milde.
# :License: Released under the terms of the `2-Clause BSD license`_, in short:
#
#    Copying and distribution of this file, with or without modification,
#    are permitted in any medium without royalty provided the copyright
#    notice and this notice are preserved.
#    This file is offered as-is, without any warranty.
#
# .. _2-Clause BSD license: http://www.spdx.org/licenses/BSD-2-Clause

openers = r"""\"\'\(\<\[\{༺༼᚛⁅⁽₍〈❨❪❬❮❰❲❴⟅⟦⟨⟪⟬⟮⦃⦅⦇⦉⦋⦍⦏⦑⦓⦕⦗⧘⧚⧼⸢⸤⸦⸨〈《「『【〔〖〘〚〝〝﴾︗︵︷︹︻︽︿﹁﹃﹇﹙﹛﹝（［｛｟｢«‘“‹⸂⸄⸉⸌⸜⸠‚„»’”›⸃⸅⸊⸍⸝⸡‛‟"""
closers = r"""\"\'\)\>\]\}༻༽᚜⁆⁾₎〉❩❫❭❯❱❳❵⟆⟧⟩⟫⟭⟯⦄⦆⦈⦊⦌⦎⦐⦒⦔⦖⦘⧙⧛⧽⸣⸥⸧⸩〉》」』】〕〗〙〛〞〟﴿︘︶︸︺︼︾﹀﹂﹄﹈﹚﹜﹞）］｝｠｣»’”›⸃⸅⸊⸍⸝⸡‛‟«‘“‹⸂⸄⸉⸌⸜⸠‚„"""
delimiters = r"\-\/\:֊־᐀᠆‐‑‒–—―⸗⸚〜〰゠︱︲﹘﹣－¡·¿;·՚՛՜՝՞՟։׀׃׆׳״؉؊،؍؛؞؟٪٫٬٭۔܀܁܂܃܄܅܆܇܈܉܊܋܌܍߷߸߹࠰࠱࠲࠳࠴࠵࠶࠷࠸࠹࠺࠻࠼࠽࠾।॥॰෴๏๚๛༄༅༆༇༈༉༊་༌།༎༏༐༑༒྅࿐࿑࿒࿓࿔၊။၌၍၎၏჻፡።፣፤፥፦፧፨᙭᙮᛫᛬᛭᜵᜶។៕៖៘៙៚᠀᠁᠂᠃᠄᠅᠇᠈᠉᠊᥄᥅᧞᧟᨞᨟᪠᪡᪢᪣᪤᪥᪦᪨᪩᪪᪫᪬᪭᭚᭛᭜᭝᭞᭟᭠᰻᰼᰽᰾᰿᱾᱿᳓‖‗†‡•‣․‥…‧‰‱′″‴‵‶‷‸※‼‽‾⁁⁂⁃⁇⁈⁉⁊⁋⁌⁍⁎⁏⁐⁑⁓⁕⁖⁗⁘⁙⁚⁛⁜⁝⁞⳹⳺⳻⳼⳾⳿⸀⸁⸆⸇⸈⸋⸎⸏⸐⸑⸒⸓⸔⸕⸖⸘⸙⸛⸞⸟⸪⸫⸬⸭⸮⸰⸱、。〃〽・꓾꓿꘍꘎꘏꙳꙾꛲꛳꛴꛵꛶꛷꡴꡵꡶꡷꣎꣏꣸꣹꣺꤮꤯꥟꧁꧂꧃꧄꧅꧆꧇꧈꧉꧊꧋꧌꧍꧞꧟꩜꩝꩞꩟꫞꫟꯫︐︑︒︓︔︕︖︙︰﹅﹆﹉﹊﹋﹌﹐﹑﹒﹔﹕﹖﹗﹟﹠﹡﹨﹪﹫！＂＃％＆＇＊，．／：；？＠＼｡､･𐄀𐄁𐎟𐏐𐡗𐤟𐤿𐩐𐩑𐩒𐩓𐩔𐩕𐩖𐩗𐩘𐩿𐬹𐬺𐬻𐬼𐬽𐬾𐬿𑂻𑂼𑂾𑂿𑃀𑃁𒑰𒑱𒑲𒑳"
closing_delimiters = r"\.\,\;\!\?"
