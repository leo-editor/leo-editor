# @+leo-ver=5-thin
# @+node:ekr.20260915043529.1: * @file ../unittests/core/test_leoMarkdown.py
"""Tests of leoMarkdown.py"""

import textwrap

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
from leo.core.leoMarkup import MarkupCommands

assert g


# @+others
# @+node:ekr.20260915043622.1: ** class TestMarkdown(LeoUnitTest)
class TestMarkdown(LeoUnitTest):
    """Test cases for leoMarkdown.py"""

    # @+others
    # @+node:ekr.20260915043717.1: *3* TestMarkdown.test_adoc
    def test_adoc(self):
        script = textwrap.dedent("""
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

        c = self.c
        ### p = c.p
        x = MarkupCommands(c)
        s = x.remove_directives(script)
        ### g.printObj(s, tag=c.p.h)  ###
        assert s == script.replace('@language html\n', '')

    # @-others


# @-others
# @-leo
