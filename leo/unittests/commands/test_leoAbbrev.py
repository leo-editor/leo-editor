# @+leo-ver=5-thin
# @+node:ekr.20260512145309.1: * @file ../unittests/commands/test_leoAbbrev.py
"""Tests of leoAbbrev.py"""

# pylint: disable=no-member
from __future__ import annotations
import re
import time
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoGui import LeoKeyEvent, StringFindTabManager
from leo.core.leoTest2 import LeoUnitTest

if TYPE_CHECKING:
    from leo.plugins.qt_text import QTextMixin

assert g


# @+others
# @+node:ekr.20260512145550.104: ** class TestAbbrev (LeoUnitTest)
class TestAbbrev(LeoUnitTest):
    def setUp(self) -> None:
        super().setUp()
        c = self.c
        c.findCommands.ftm = StringFindTabManager(c)

    # @+others
    # @+node:ekr.20260512164351.1: *3* TestAbbrev.test_multiline_abbreviations
    def test_multiline_abbreviations(self):

        c = self.c
        p = c.p
        x = c.abbrevCommands
        x.abbrevs = {}

        # These must be the definition munged by c.config.getData.
        definitions = (
            'details;;=<details><summary><b><|Title|></b></summary>\n<br>\n\n</details>',
        )  # fmt: skip

        for definition in definitions:
            x.addAbbrevHelper(definition)

        def test(kind, results, expected) -> None:
            assert results == expected, (
                f"{kind}\n"
                f"expected: {expected!r}\n"
                f"     got: {results!r}"
            )  # fmt: skip

        # Test bodies.
        if 1:
            w = c.frame.body.wrapper
            for definition in definitions:
                i = definition.find(';=')
                contents = definition[:i]
                expected = definition[i + 2 :]
                p.b = contents
                w.setInsertPoint(len(contents), contents)
                event = LeoKeyEvent(c, char=';', binding=';', w=w)
                x.expandAbbrev(event=event, stroke=None)
                test('body', p.b, expected)
                test('body', w.getAllText(), expected)

        # Test headlines
        if 1:
            for definition in definitions:
                c.editHeadline()
                w = c.headline_wrapper(p)
                i = definition.find(';=')
                contents = definition[:i]
                expected = definition[i + 2 :]
                p.h = contents
                w.setInsertPoint(len(contents), contents)
                event = LeoKeyEvent(c, char=';', binding=';', w=w)
                x.expandAbbrev(event=event, stroke=None)
                test('head', w.getAllText(), expected)
                c.endEditing()
                expected_p_h = expected.replace('\n', ' ').replace('  ', ' ')
                test('head', p.h, expected_p_h)

    # @+node:ekr.20260518063848.1: *3* TestAbbrev.test_find_command_selects_place_holder
    def test_find_command_selects_place_holder(self):

        c = self.c
        p = c.p
        finder = c.findCommands
        x = c.abbrevCommands
        x.abbrevs = {}

        # These must be the definition munged by c.config.getData.
        definitions = (
            'details;;=<details><summary><b><|Title|></b></summary>\n<br>\n\n</details>',
            'html;;='
                '<html>\n<head>\n<title><|title|></title>\n'
                '<style>\n</style>\n</head>\n<body>\n<|content|>\n</body>\n</html>',
        )  # fmt: skip

        expected_selections = (
            '<|Title|>',
            '<|title|>',
        )

        for definition in definitions:
            x.addAbbrevHelper(definition)

        def test_contents(kind, results: str, expected: str) -> None:
            assert results == expected, (
                f"{kind}\n"
                f"expected: {expected!r}\n"
                f"     got: {results!r}"
            )  # fmt: skip

        def test_selection(kind, w: QTextMixin, expected: str) -> None:
            # See LeoFind.show_success.
            results = w.getSelectedText()
            # g.trace(kind, repr(results), w, g.truncate(w.getAllText().replace('\n', '\\n'), 40))
            assert results == expected, (
                f"{kind} id: {id(w)}\n"
                f"expected: {expected!r}\n"
                f"     got: {results!r}"
            )  # fmt: skip

        # Test bodies.
        if 1:
            w = c.frame.body.wrapper
            for test_number, definition in enumerate(definitions):
                finder.in_headline = False
                i = definition.find(';=')
                contents = definition[:i]
                expected = definition[i + 2 :]
                p.b = contents
                w.setInsertPoint(len(contents), contents)
                event = LeoKeyEvent(c, char=';', binding=';', w=w)
                x.expandAbbrev(event=event, stroke=None)
                test_contents('body', p.b, expected)
                test_contents('body', w.getAllText(), expected)
                test_selection('body', w, expected_selections[test_number])

        # Test headlines
        if 1:
            for test_number, definition in enumerate(definitions):
                finder.in_headline = True
                c.editHeadline()
                w = c.headline_wrapper(p)
                i = definition.find(';=')
                contents = definition[:i]
                expected = definition[i + 2 :]
                p.h = contents
                w.setInsertPoint(len(contents), contents)
                event = LeoKeyEvent(c, char=';', binding=';', w=w)
                x.expandAbbrev(event=event, stroke=None)
                test_contents('head', w.getAllText(), expected)
                test_selection('head', w, expected_selections[test_number])
                c.endEditing()
                expected_p_h = expected.replace('\n', ' ').replace('  ', ' ')
                test_contents('head', p.h, expected_p_h)

    # @+node:ekr.20260512173657.1: *3* TestAbbrev.test_scripting_abbreviations
    def test_scripting_abbreviations(self):

        c = self.c
        p = c.p
        x = c.abbrevCommands
        x.abbrevs = {}
        x.scripting_enabled = True
        c.abbrev_subst_env['time'] = time

        # These must be the definition munged by c.config.getData.
        definitions = (
            'date;;={|{x=time.strftime("%Y/%m/%d")}|}',
        )  # fmt: skip

        for definition in definitions:
            x.addAbbrevHelper(definition)

        pattern = r'[0-9]{4}/[0-9]{2}/[0-9]{2}'

        def test(results: str) -> None:
            assert re.match(pattern, results), f"results: {results!r} regex: {pattern!r}"

        # Test the body.
        w = c.frame.body.wrapper
        for definition in definitions:
            i = definition.find(';=')
            p.b = contents = definition[:i]
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(w.getAllText())
            test(p.b)

        # Test headlines.
        for definition in definitions:
            c.editHeadline()
            w = c.headline_wrapper(p)
            i = definition.find(';=')
            p.h = contents = definition[:i]
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(w.getAllText())
            c.endEditing()
            test(p.h)

    # @+node:ekr.20260512150121.1: *3* TestAbbrev.test_simple_abbreviations
    def test_simple_abbreviations(self):

        c = self.c
        p = c.p
        x = c.abbrevCommands

        # Set the ivars by hand insead of with settings.
        x.abbrevs = {}
        definitions = (
            'ex;;=!',
            'fmt;;=  # fmt: skip',
        )  # fmt: skip\n'
        for definition in definitions:
            x.addAbbrevHelper(definition)

        table = (
            ('ex;',         '!'),
            ('whateverex;', 'whatever!'),
            ('fmt;',        '  # fmt: skip'),
            (')fmt;',       ')  # fmt: skip'),
        )  # fmt: skip

        def test(results, expected) -> None:
            assert results == expected, f"expected: {expected!r} got: {results!r}"

        # Test body.
        if 1:
            w = c.frame.body.wrapper
            for contents, expected in table:
                p.b = contents
                w.setInsertPoint(len(contents), contents)
                event = LeoKeyEvent(c, char=';', binding=';', w=w)
                x.expandAbbrev(event=event, stroke=None)
                test(p.b, expected)
                test(w.getAllText(), expected)

        # Test headlines.
        for contents, expected in table:
            c.editHeadline()
            w = c.headline_wrapper(p)
            p.h = contents
            w.setAllText(contents)
            w.setInsertPoint(len(contents), contents)
            event = LeoKeyEvent(c, char=';', binding=';', w=w)
            x.expandAbbrev(event=event, stroke=None)
            test(w.getAllText(), expected)
            c.endEditing()
            test(p.h, expected)

    # @+node:ekr.20210905064816.3: *3* TestAbbrev.test_addAbbrevHelper
    def test_addAbbrevHelper(self):
        c = self.c
        f = c.abbrevCommands.addAbbrevHelper
        d = c.abbrevCommands.abbrevs

        # New in Leo 4.10: whitespace (blank,tab,newline) *is* significant in definitions.
        table = (
            ('ut1',  'ut1=aa',       'aa'),
            # ('ut2','ut2 =bb',      'bb'),
            ('ut3',  'ut3=cc=dd',    'cc=dd'),
            ('ut4',  'ut4= ee',      ' ee'),
            ('ut5',  'ut5= ff = gg', ' ff = gg'),
            ('ut6',  'ut6= hh==ii',  ' hh==ii'),
            ('ut7',  'ut7=j=k',      'j=k'),
            ('ut8',  'ut8=l==m',     'l==m'),
            ('@ut1', '@ut1=@a',      '@a'),
        )  # fmt: skip
        for name, s, expected in table:
            for s2, kind in ((s, '(no nl)'), (s + '\n', '(nl)')):
                f(s2, tag='unit-test')
                result = d.get(name)
                self.assertEqual(result, expected, msg=kind)

    # @-others


# @-others
# @-leo
