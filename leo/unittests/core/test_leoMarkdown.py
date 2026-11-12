# @+leo-ver=5-thin
# @+node:ekr.20260915043529.1: * @file ../unittests/core/test_leoMarkdown.py
"""Tests of leoMarkdown.py"""

import io
from shutil import which

# from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
from leo.core.leoMarkup import MarkupCommands


# @+others
# @+node:ekr.20260915043622.1: ** class TestMarkdown(LeoUnitTest)
class TestMarkdown(LeoUnitTest):
    """Test cases for leoMarkdown.py"""

    def setUp(self):
        super().setUp()
        if not which('asciidoc3'):
            self.skipTest('Requires asciidoc3')

    # @+others
    # @+node:ekr.20260916125105.1: *3* TestMarkdown.test_write_body
    def test_write_body(self):
        c = self.c
        p = c.p
        # @+<< define body >>
        # @+node:ekr.20260916133329.1: *4* << define body >>
        body = self.prep(
        """
            Some intro text before the first source block.

            .App.svelte parent component
            [source,html]
            ----
            ATlanguage html
            <script>let message = $state('hello');</script>
            ----

            .FancyInput.svelte child component
            [source,html]
            ----
            ATlanguage html
            <input bind:value={value} />
            ----
        """).replace('AT', '@')  # fmt: skip
        # @-<< define body >>
        # @+<< define expected >>
        # @+node:ekr.20260916133712.1: *4* << define expected >>
        expected = self.prep(
        """
            = child
            Some intro text before the first source block.

            .App.svelte parent component
            [source,html]
            ----
            <script>let message = $state('hello');</script>
            ----

            .FancyInput.svelte child component
            [source,html]
            ----
            <input bind:value={value} />
            ----
        """)  # fmt: skip
        # @-<< define expected >>
        p.h = '@adoc dummy'
        p.b = '@language asciidoc\n'
        child = p.insertAsLastChild()
        child.h = 'child'
        child.b = body
        x = MarkupCommands(c)
        s = x.remove_directives(body)
        x.kind = 'adoc'
        x.output_file = io.StringIO(s)
        x.write_root(p)
        result = x.output_file.getvalue()
        # g.printObj(expected, tag='expected')
        # g.printObj(result, tag='result')
        self.assertEqual(result, expected)

    # @-others


# @-others
# @-leo
