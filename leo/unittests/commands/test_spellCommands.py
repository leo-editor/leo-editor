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

        c = self.c

        # Create test classes.
        class TestEnchantWrapper:

            def __init__(self, c):
                self.c = c
                self.language = 'en_US'
                self.d: dict[str, str] = {}
                g.app.spellDict = self.d

        x = TestEnchantWrapper(c)
        if 0:
            g.trace(x)


    #@-others
#@-others
#@-leo
