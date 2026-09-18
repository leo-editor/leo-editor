"""Tests of leoMarkup.py"""

import io

from leo.core import leoGlobals as g
from leo.core import leoMarkup
from leo.core.leoTest2 import LeoUnitTest


class TestMarkup(LeoUnitTest):
    """Test cases for leoMarkup.py"""

    def test_adoc_preserves_body_with_multiple_language_directives(self):
        """
        The @adoc command must write the *entire* body of a node.

        Regression test for a node that contains two or more @language
        directives.  g.getScript() used to call g.extractExecutableString(),
        which:

        (a) discarded all text *before* the first @language directive, and
        (b) discarded the text of every section whose @language does not match
            the language in effect.

        The @adoc command now calls g.getScript(..., useExtraction=False).
        """
        c, p = self.c, self.c.p
        p.b = self.prep(
            """
            intro text

            .App.svelte
            [source,html]
            ----
            @language html
            <script>let message = $state('hello');</script>
            ----

            .FancyInput.svelte
            [source,html]
            ----
            @language html
            <input bind:value={value} />
            ----
            """
        )
        m = leoMarkup.MarkupCommands(c)
        m.kind = 'adoc'
        m.output_file = io.StringIO()

        # g.extractExecutableString is a no-op while g.unitTesting is True,
        # so turn it off to exercise the real code path.
        old_unit_testing = g.unitTesting
        g.unitTesting = False
        try:
            m.write_body(p)
        finally:
            g.unitTesting = old_unit_testing

        result = m.output_file.getvalue()
        # Text before the first @language directive must be preserved.
        self.assertIn('intro text', result)
        self.assertIn('[source,html]', result)
        # The first @language section must be preserved.
        self.assertIn('let message', result)
        # Text after the second @language directive must be preserved.
        self.assertIn('.FancyInput.svelte', result)
        self.assertIn('bind:value', result)
        # The @language directives themselves must be removed.
        self.assertNotIn('@language', result)

    def test_getScript_useExtraction(self):
        """
        g.getScript(..., useExtraction=False) must not drop text that
        g.getScript(..., useExtraction=True) would drop.
        """
        c, p = self.c, self.c.p
        p.b = self.prep(
            """
            intro text
            @language html
            <script>one</script>
            @language html
            <script>two</script>
            """
        )
        old_unit_testing = g.unitTesting
        g.unitTesting = False
        try:
            with_extraction = g.getScript(c, p, useSentinels=False, useExtraction=True)
            without_extraction = g.getScript(c, p, useSentinels=False, useExtraction=False)
        finally:
            g.unitTesting = old_unit_testing

        # Without extraction, all of the text is kept.
        self.assertIn('intro text', without_extraction)
        self.assertIn('<script>one</script>', without_extraction)
        self.assertIn('<script>two</script>', without_extraction)
        # With extraction, the leading text is dropped.
        self.assertNotIn('intro text', with_extraction)
