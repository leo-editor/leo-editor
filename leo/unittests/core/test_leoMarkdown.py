# @+leo-ver=5-thin
# @+node:ekr.20260915043529.1: * @file ../unittests/core/test_leoMarkdown.py
"""Tests of leoMarkdown.py"""

from shutil import which
import textwrap

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

assert g


# @+others
# @+node:ekr.20260915043622.1: ** class TestMarkdown(LeoUnitTest)
class TestMarkdown(LeoUnitTest):
    """Test cases for leoMarkdown.py"""

    def setUp(self):
        if not which('asciidoctor') and not which('asciidoc3'):
            self.skipTest('Markdown tests require asciidoctor or asciidoc3')

    # @+others
    # @+node:ekr.20260915043717.1: *3* TestMarkdown.test_adoc
    def test_adoc(self):
        s = textwrap.dedent("""
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
    """).replace('AT', '@')

        assert s

    # @-others


# @-others
# @-leo
