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

        if not g.isWindows:
            self.skipTest('Requires Windows')

        try:
            import enchant
            assert enchant
        except Exception:  # May throw WinError(!)
            self.skipTest('Requires enchant')

        from leo.core.leoCommands import Commands as Cmdr
        from leo.commands.spellCommands import SpellTabHandler

        c = self.c
        p = c.p

        # Create test classes.
        class TestEnchantWrapper:

            def __init__(self, c: Cmdr) -> None:
                self.c = c
                # This dict simulates what process_word should return.
                self.d: dict[str, list[str]] = {
                    'abc9': ['abc'],
                    'beginx': ['begin'],
                    "we'lll": ["we'll", 'well'],
                    "Leo's": ['Leo', 'Leos'],
                    'selll': ['sell'],
                }

            def process_word(self, word: str) -> list[str]:
                """Retrieve from self.d."""
                # Assume all words not in self.d are *valid*
                return self.d.get(word, [word])

        # Monkey-patch the controller into the handler.
        handler = SpellTabHandler(c, tabName='Test Spell Tab')
        handler.spellController = TestEnchantWrapper(c)

        # sel_1  selll_1
        # a_b_c

        table = (
             # Should not be checked.
            ('abc9: https://test1', 'abc'),
            # Should be checked.
            ("Leo's: https://test2", 'Leo'),
            ("we'lll", "we'll"),
            (r'\begin', 'begin'),
            ('beginx', 'begin'),
            (r'\beginx', 'begin'),
            (r'\bibliographystyle{acm}', 'bibliographystyle'),
            # Tests of munging.
            ('_Insert_indexterm__140664580.txt', 'Insert_indexterm'),
            ('sel_1', 'sel'),
            ('selll_1', 'sell'),
            ('a_b_c', 'a_b_c'),
        )
        for line, expected in table:
            p.b = line + '\n'
            result = handler.find()
            assert result == expected, (repr(result), repr(expected))
    #@-others
#@-others
#@-leo
