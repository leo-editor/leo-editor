#@+leo-ver=5-thin
#@+node:ekr.20230916141635.1: * @file ../unittests/commands/test_spellCommands.py
"""
New unit tests for Leo's outline commands.

Older tests are in unittests/core/test_leoNodes.py
"""
from leo.core.leoTest2 import LeoUnitTest
from leo.core import leoGlobals as g
assert g


#@+others
#@+node:ekr.20230916141635.2: ** class TestSpellCommands(LeoUnitTest)
class TestSpellCommands(LeoUnitTest):
    """
    Unit tests for Leo's outline commands.
    """

    #@+others
    #@+node:ekr.20230916141635.3: *3* TestSpellCommands.test_SpellTabHandler_find
    def test_SpellTabHandler_find(self):

        from leo.core.leoCommands import Commands as Cmdr
        from leo.commands.spellCommands import SpellTabHandler

        c = self.c
        p = c.p

        # Create test classes.
        class TestEnchantWrapper:

            def __init__(self, c: Cmdr) -> None:
                self.c = c
                self.d: dict[str, str] = {}
                ### self.language = 'en_US'
                ### g.app.spellDict = self.d

            def process_word(self, word: str) -> list[str]:
                g.trace(word)
                return [word]

        handler = SpellTabHandler(c, tabName='Test Spell Tab')
        handler.loaded = True
        handler.spellController = TestEnchantWrapper(c)

        # \beginx
        # \begin
        # \bibliographystyle{acm}
        # \bibliography{myBibliography}

        # `PR #3509`: Improve rust importer.
        # _Insert_indexterm__140664580.txt

        # we'lll we're we'll
        # sel_1  selll_1
        # a_b_c

        table = (
             # Should not be checked.
            'abc9: https://test1',
            # Should be checked.
            "Leo's: https://test2",
        )
        for word in table:
            p.b = word + '\n'
            handler.find()
    #@-others
#@-others
#@-leo
