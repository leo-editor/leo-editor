#@+leo-ver=5-thin
#@+node:ekr.20201202144422.1: * @file ../unittests/commands/test_editCommands.py
"""Tests of leo.commands.editCommands."""
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20210829060957.1: ** class TestEditCommands(LeoUnitTest)
class TestEditCommands(LeoUnitTest):
    """Unit tests for leo/commands/editCommands.py."""
    # For pylint.
    before_p = after_p = parent_p = tempNode = None
    #@+others
    #@+node:ekr.20201129161726.5: *3* TestEditCommands.run_test
    def run_test(self,
            before_b: str,
            after_b: str,  # before/after body text.
            before_sel: str,
            after_sel: str,  # before and after selection ranges.
            command_name: str,
            directives: str='',
            dedent: bool=True,
        ):
        """
        A helper for many commands tests.
        """
        c = self.c

        def toInt(s):
            return g.toPythonIndex(before_b, s)

        # For shortDescription().
        self.command_name = command_name
        # Compute the result in tempNode.b
        command = c.commandsDict.get(command_name)
        assert command, f"no command: {command_name}"
        # Set the text.
        if dedent:
            parent_b = textwrap.dedent(directives)
            before_b = textwrap.dedent(before_b)
            after_b = textwrap.dedent(after_b)
        else:
            # The unit test is responsible for all indentation.
            parent_b = directives
        self.parent_p.b = parent_b
        self.tempNode.b = before_b
        self.before_p.b = before_b
        self.after_p.b = after_b
        # Set the selection range and insert point.
        w = c.frame.body.wrapper
        i, j = before_sel
        i, j = toInt(i), toInt(j)
        w.setSelectionRange(i, j, insert=j)
        # Run the command!
        c.doCommandByName(command_name)
        self.assertEqual(self.tempNode.b, self.after_p.b, msg=command_name)
    #@+node:ekr.20201201084621.1: *3* TestEditCommands.setUp
    def setUp(self):
        """Create the nodes in the commander."""
        super().setUp()
        c = self.c
        # Create top-level parent node.
        self.parent_p = self.root_p.insertAsLastChild()
        # Create children of the parent node.
        self.tempNode = self.parent_p.insertAsLastChild()
        self.before_p = self.parent_p.insertAsLastChild()
        self.after_p = self.parent_p.insertAsLastChild()
        self.tempNode.h = 'tempNode'
        self.before_p.h = 'before'
        self.after_p.h = 'after'
        c.selectPosition(self.tempNode)

    # def tearDown(self):
        # self.c = None
    #@+node:ekr.20201130091020.1: *3* TestEditCommands: Commands...
    #@+node:ekr.20210829061326.1: *4* Commands A-B
    #@+node:ekr.20201130090918.1: *5* add-space-to-lines
    def test_add_space_to_lines(self):
        """Test case for add-space-to-lines"""
        before_b = """\
    first line
    line 1
        line a
    line b
    last line
    """
        after_b = """\
    first line
     line 1
         line a
     line b
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.0", "4.6"),
            after_sel=("2.0", "4.7"),
            command_name="add-space-to-lines",
        )
    #@+node:ekr.20201130090918.2: *5* add-tab-to-lines
    def test_add_tab_to_lines(self):
        """Test case for add-tab-to-lines"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
        line 1
            line a
                line b
        line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.0", "5.6"),
            after_sel=("2.0", "5.10"),
            command_name="add-tab-to-lines",
        )
    #@+node:ekr.20201130090918.3: *5* back-char
    def test_back_char(self):
        """Test case for back-char"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.8", "3.8"),
            after_sel=("3.7", "3.7"),
            command_name="back-char",
        )
    #@+node:ekr.20201130090918.4: *5* back-char-extend-selection
    def test_back_char_extend_selection(self):
        """Test case for back-char-extend-selection"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("4.12", "4.12"),
            after_sel=("4.11", "4.12"),
            command_name="back-char-extend-selection",
        )
    #@+node:ekr.20201130090918.5: *5* back-paragraph
    def test_back_paragraph(self):
        """Test case for back-paragraph"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("9.0", "9.0"),
            after_sel=("6.7", "6.7"),
            command_name="back-paragraph",
        )
    #@+node:ekr.20201130090918.6: *5* back-paragraph-extend-selection
    def test_back_paragraph_extend_selection(self):
        """Test case for back-paragraph-extend-selection"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("9.0", "9.5"),
            after_sel=("6.7", "9.5"),
            command_name="back-paragraph-extend-selection",
        )
    #@+node:ekr.20201130090918.7: *5* back-sentence
    def test_back_sentence(self):
        """Test case for back-sentence"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.169", "3.169"),
            after_sel=("3.143", "3.143"),
            command_name="back-sentence",
        )
    #@+node:ekr.20201130090918.8: *5* back-sentence-extend-selection
    def test_back_sentence_extend_selection(self):
        """Test case for back-sentence-extend-selection"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.208", "3.208"),
            after_sel=("3.143", "3.208"),
            command_name="back-sentence-extend-selection",
        )
    #@+node:ekr.20201130090918.12: *5* back-to-home (at end of line)
    def test_back_to_home_at_end_of_line(self):
        """Test case for back-to-home (at end of line)"""
        before_b = """\
    if a:
        b = 'xyz'
    """
        after_b = """\
    if a:
        b = 'xyz'
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.12", "2.12"),
            after_sel=("2.4", "2.4"),
            command_name="back-to-home",
        )
    #@+node:ekr.20201130090918.11: *5* back-to-home (at indentation
    def test_back_to_home_at_indentation(self):
        """Test case for back-to-home (at indentation"""
        before_b = """\
    if a:
        b = 'xyz'
    """
        after_b = """\
    if a:
        b = 'xyz'
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.4", "2.4"),
            after_sel=("2.0", "2.0"),
            command_name="back-to-home",
        )
    #@+node:ekr.20201130090918.10: *5* back-to-home (at start of line)
    def test_back_to_home_at_start_of_line(self):
        """Test case for back-to-home (at start of line)"""
        before_b = """\
    if a:
        b = 'xyz'
    """
        after_b = """\
    if a:
        b = 'xyz'
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.0", "2.0"),
            after_sel=("2.4", "2.4"),
            command_name="back-to-home",
        )
    #@+node:ekr.20201130090918.9: *5* back-to-indentation
    def test_back_to_indentation(self):
        """Test case for back-to-indentation"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("4.13", "4.13"),
            after_sel=("4.8", "4.8"),
            command_name="back-to-indentation",
        )
    #@+node:ekr.20201130090918.13: *5* back-word
    def test_back_word(self):
        """Test case for back-word"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.183", "1.183"),
            after_sel=("1.178", "1.178"),
            command_name="back-word",
        )
    #@+node:ekr.20201130090918.14: *5* back-word-extend-selection
    def test_back_word_extend_selection(self):
        """Test case for back-word-extend-selection"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.342", "3.342"),
            after_sel=("3.332", "3.342"),
            command_name="back-word-extend-selection",
        )
    #@+node:ekr.20201130090918.15: *5* backward-delete-char
    def test_backward_delete_char(self):
        """Test case for backward-delete-char"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first lie
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.9", "1.9"),
            after_sel=("1.8", "1.8"),
            command_name="backward-delete-char",
        )
    #@+node:ekr.20201130090918.16: *5* backward-delete-char  (middle of line)
    def test_backward_delete_char__middle_of_line(self):
        """Test case for backward-delete-char  (middle of line)"""
        before_b = """\
    first line
    last line
    """
        after_b = """\
    firstline
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.6", "1.6"),
            after_sel=("1.5", "1.5"),
            command_name="backward-delete-char",
        )
    #@+node:ekr.20201130090918.17: *5* backward-delete-char (last char)
    def test_backward_delete_char_last_char(self):
        """Test case for backward-delete-char (last char)"""
        before_b = """\
    first line
    last line
    """
        after_b = """\
    first line
    last lin
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.9", "2.9"),
            after_sel=("2.8", "2.8"),
            command_name="backward-delete-char",
        )
    #@+node:ekr.20201130090918.18: *5* backward-delete-word (no selection)
    def test_backward_delete_word_no_selection(self):
        """Test case for backward-delete-word (no selection)"""
        before_b = """\
    aaaa bbbb cccc dddd
    """
        after_b = """\
    aaaa cccc dddd
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.10", "1.10"),
            after_sel=("1.5", "1.5"),
            command_name="backward-delete-word",
        )
    #@+node:ekr.20201130090918.19: *5* backward-delete-word (selection)
    def test_backward_delete_word_selection(self):
        """Test case for backward-delete-word (selection)"""
        before_b = """\
    aaaa bbbb cccc dddd
    """
        after_b = """\
    aaaa bbcc dddd
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.7", "1.12"),
            after_sel=("1.7", "1.7"),
            command_name="backward-delete-word",
        )
    #@+node:ekr.20201130090918.20: *5* backward-kill-paragraph
    def test_backward_kill_paragraph(self):
        """Test case for backward-kill-paragraph"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("9.0", "9.0"),
            after_sel=("7.0", "7.0"),
            command_name="backward-kill-paragraph",
        )
    #@+node:ekr.20201130090918.21: *5* backward-kill-sentence
    def test_backward_kill_sentence(self):
        """Test case for backward-kill-sentence"""
        before_b = """\
    This is the first sentence.  This
    is the second sentence.  And
    this is the last sentence.
    """
        after_b = """\
    This is the first sentence.  This
    is the second sentence.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.2", "3.2"),
            after_sel=("2.23", "2.23"),
            command_name="backward-kill-sentence",
        )
    #@+node:ekr.20201130090918.22: *5* backward-kill-word
    def test_backward_kill_word(self):
        """Test case for backward-kill-word"""
        before_b = """\
    This is the first sentence.  This
    is the second sentence.  And
    this is the last sentence.
    """
        after_b = """\
    This is the first sentence.  This
    is the second sentence.  And
    this  the last sentence.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.7", "3.7"),
            after_sel=("3.5", "3.5"),
            command_name="backward-kill-word",
        )
    #@+node:ekr.20201130090918.23: *5* beginning-of-buffer
    def test_beginning_of_buffer(self):
        """Test case for beginning-of-buffer"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("5.56", "5.56"),
            after_sel=("1.0", "1.0"),
            command_name="beginning-of-buffer",
        )
    #@+node:ekr.20201130090918.24: *5* beginning-of-buffer-extend-selection
    def test_beginning_of_buffer_extend_selection(self):
        """Test case for beginning-of-buffer-extend-selection"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.423", "3.423"),
            after_sel=("1.0", "3.423"),
            command_name="beginning-of-buffer-extend-selection",
        )
    #@+node:ekr.20201130090918.25: *5* beginning-of-line
    def test_beginning_of_line(self):
        """Test case for beginning-of-line"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.10", "3.10"),
            after_sel=("3.0", "3.0"),
            command_name="beginning-of-line",
        )
    #@+node:ekr.20201130090918.26: *5* beginning-of-line-extend-selection
    def test_beginning_of_line_extend_selection(self):
        """Test case for beginning-of-line-extend-selection"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("4.10", "4.10"),
            after_sel=("4.0", "4.10"),
            command_name="beginning-of-line-extend-selection",
        )
    #@+node:ekr.20210829061337.1: *4* Commands C-E
    #@+node:ekr.20201130090918.27: *5* capitalize-word
    def test_capitalize_word(self):
        """Test case for capitalize-word"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        Line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.6", "3.6"),
            after_sel=("3.6", "3.6"),
            command_name="capitalize-word",
        )
    #@+node:ekr.20201130090918.28: *5* center-line
    def test_center_line(self):
        """Test case for center-line"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related,
    leading to around 500 deaths per year and nearly $14 billion in damage.
    StormReady, a program started in 1999 in Tulsa, OK,
    helps arm America's communities with the communication and safety
    skills needed to save lives and property– before and during the event.
    StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related,
    leading to around 500 deaths per year and nearly $14 billion in damage.
    StormReady, a program started in 1999 in Tulsa, OK,
    helps arm America's communities with the communication and safety
    skills needed to save lives and property– before and during the event.
    StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.0", "9.0"),
            after_sel=("3.0", "9.0"),
            command_name="center-line",
        )
    #@+node:ekr.20201130090918.29: *5* center-region
    def test_center_region(self):
        """Test case for center-region"""
        before_b = """\
    Some 90% of all presidentially declared disasters are weather related,
    leading to around 500 deaths per year and nearly $14 billion in damage.
    StormReady, a program started in 1999 in Tulsa, OK,
    helps arm America's communities with the communication and safety
    skills needed to save lives and property– before and during the event.
    StormReady helps community leaders and emergency managers strengthen local safety programs.
    """
        after_b = """\
    Some 90% of all presidentially declared disasters are weather related,
    leading to around 500 deaths per year and nearly $14 billion in damage.
             StormReady, a program started in 1999 in Tulsa, OK,
      helps arm America's communities with the communication and safety
    skills needed to save lives and property– before and during the event.
    StormReady helps community leaders and emergency managers strengthen local safety programs.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "7.0"),
            after_sel=("1.0", "7.0"),
            command_name="center-region",
            directives="@pagewidth 70",
        )
    #@+node:ekr.20201130090918.30: *5* clean-lines
    def test_clean_lines(self):
        """Test case for clean-lines"""
        before_b = textwrap.dedent("""\
            # Should remove all trailing whitespace.

            a = 2

                b = 3
                c  = 4
            d = 5
            e = 6
            x
            """)
        after_b = before_b
        # Add some trailing ws to before_b
        i = 1 + before_b.find('3')
        before_b = before_b[:i] + '  ' + before_b[i:]
        self.assertNotEqual(before_b, after_b)
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("1.0", "1.0"),
            command_name="clean-lines",
        )
    #@+node:ekr.20201130090918.31: *5* clear-selected-text
    def test_clear_selected_text(self):
        """Test case for clear-selected-text"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line    line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.4", "4.4"),
            after_sel=("2.4", "2.4"),
            command_name="clear-selected-text",
        )
    #@+node:ekr.20201130090918.32: *5* count-region
    def test_count_region(self):
        """Test case for count-region"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.4", "4.8"),
            after_sel=("2.4", "4.8"),
            command_name="count-region",
        )
    #@+node:ekr.20201130090918.33: *5* delete-char
    def test_delete_char(self):
        """Test case for delete-char"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    firstline
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.5", "1.5"),
            after_sel=("1.5", "1.5"),
            command_name="delete-char",
        )
    #@+node:ekr.20201130090918.34: *5* delete-indentation
    def test_delete_indentation(self):
        """Test case for delete-indentation"""
        before_b = """\
    first line
        line 1
    last line
    """
        after_b = """\
    first line
    line 1
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.8", "2.8"),
            after_sel=("2.4", "2.4"),
            command_name="delete-indentation",
        )
    #@+node:ekr.20201130090918.35: *5* delete-spaces
    def test_delete_spaces(self):
        """Test case for delete-spaces"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
    line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.2", "3.2"),
            after_sel=("3.0", "3.0"),
            command_name="delete-spaces",
        )
    #@+node:ekr.20201130090918.36: *5* do-nothing
    def test_do_nothing(self):
        """Test case for do-nothing"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("1.0", "1.0"),
            command_name="do-nothing",
        )
    #@+node:ekr.20201130090918.37: *5* downcase-region
    def test_downcase_region(self):
        """Test case for downcase-region"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. stormready, a program started in 1999 in tulsa, ok, helps arm america's communities with the communication and safety skills needed to save lives and property– before and during the event. stormready helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.0", "4.0"),
            after_sel=("3.0", "4.0"),
            command_name="downcase-region",
        )
    #@+node:ekr.20201130090918.38: *5* downcase-word
    def test_downcase_word(self):
        """Test case for downcase-word"""
        before_b = """\
    XYZZY line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    xyzzy line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.4", "1.4"),
            after_sel=("1.4", "1.4"),
            command_name="downcase-word",
        )
    #@+node:ekr.20201130090918.39: *5* end-of-buffer
    def test_end_of_buffer(self):
        """Test case for end-of-buffer"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.3", "1.3"),
            after_sel=("7.0", "7.0"),
            command_name="end-of-buffer",
        )
    #@+node:ekr.20201130090918.40: *5* end-of-buffer-extend-selection
    def test_end_of_buffer_extend_selection(self):
        """Test case for end-of-buffer-extend-selection"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("1.0", "7.0"),
            command_name="end-of-buffer-extend-selection",
        )
    #@+node:ekr.20201130090918.41: *5* end-of-line
    def test_end_of_line(self):
        """Test case for end-of-line"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("1.10", "1.10"),
            command_name="end-of-line",
        )
    #@+node:ekr.20201130090918.44: *5* end-of-line (blank last line)
    def test_end_of_line_blank_last_line(self):
        """Test case for end-of-line (blank last line)"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last non-blank line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last non-blank line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("7.0", "7.0"),
            after_sel=("7.0", "7.0"),
            command_name="end-of-line",
        )
    #@+node:ekr.20201130090918.43: *5* end-of-line (internal blank line)
    def test_end_of_line_internal_blank_line(self):
        """Test case for end-of-line (internal blank line)"""
        before_b = """\
    first line

    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line

    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.0", "2.0"),
            after_sel=("2.0", "2.0"),
            command_name="end-of-line",
        )
    #@+node:ekr.20201130090918.45: *5* end-of-line (single char last line)
    def test_end_of_line_single_char_last_line(self):
        """Test case for end-of-line (single char last line)"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last non-blank line

    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last non-blank line

    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("7.0", "7.0"),
            after_sel=("7.1", "7.1"),
            command_name="end-of-line",
        )
    #@+node:ekr.20201130090918.42: *5* end-of-line 2
    def test_end_of_line_2(self):
        """Test case for end-of-line 2"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("6.0", "6.0"),
            after_sel=("6.9", "6.9"),
            command_name="end-of-line",
        )
    #@+node:ekr.20201130090918.46: *5* end-of-line-extend-selection
    def test_end_of_line_extend_selection(self):
        """Test case for end-of-line-extend-selection"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.0", "3.0"),
            after_sel=("3.0", "3.10"),
            command_name="end-of-line-extend-selection",
        )
    #@+node:ekr.20201130090918.47: *5* end-of-line-extend-selection (blank last line)
    def test_end_of_line_extend_selection_blank_last_line(self):
        """Test case for end-of-line-extend-selection (blank last line)"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last non-blank line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last non-blank line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("7.0", "7.0"),
            after_sel=("7.0", "7.0"),
            command_name="end-of-line-extend-selection",
        )
    #@+node:ekr.20201130090918.48: *5* exchange-point-mark
    def test_exchange_point_mark(self):
        """Test case for exchange-point-mark"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.10"),
            after_sel=("1.0", "1.10"),
            command_name="exchange-point-mark",
        )
    #@+node:ekr.20201130090918.49: *5* extend-to-line
    def test_extend_to_line(self):
        """Test case for extend-to-line"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.3", "3.3"),
            after_sel=("3.0", "3.10"),
            command_name="extend-to-line",
        )
    #@+node:ekr.20201130090918.50: *5* extend-to-paragraph
    def test_extend_to_paragraph(self):
        """Test case for extend-to-paragraph"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("9.0", "9.0"),
            after_sel=("8.0", "13.33"),
            command_name="extend-to-paragraph",
        )
    #@+node:ekr.20201130090918.51: *5* extend-to-sentence
    def test_extend_to_sentence(self):
        """Test case for extend-to-sentence"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.5", "3.5"),
            after_sel=("1.395", "3.142"),
            command_name="extend-to-sentence",
        )
    #@+node:ekr.20201130090918.52: *5* extend-to-word
    def test_extend_to_word(self):
        """Test case for extend-to-word"""
        before_b = """\
    first line
    line 1
        line_24a a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line_24a a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.10", "3.10"),
            after_sel=("3.4", "3.12"),
            command_name="extend-to-word",
        )
    #@+node:ekr.20210829062134.1: *4* Commands F-L
    #@+node:ekr.20201130090918.56: *5* fill-paragraph
    def test_fill_paragraph(self):
        """Test case for fill-paragraph"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Services StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially
    declared disasters are weather related,
    leading to around 500 deaths per year
    and nearly $14 billion in damage.
    StormReady, a program
    started in 1999 in Tulsa, OK,
    helps arm America's
    communities with the communication and
    safety skills needed to save lives and
    property--before and during the event.
    StormReady helps community leaders and
    emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Services StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property--before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.0", "3.7"),
            after_sel=("10.0", " 10.0"),
            command_name="fill-paragraph",
            directives="@pagewidth 80",
        )
    #@+node:ekr.20201130090918.53: *5* finish-of-line
    def test_finish_of_line(self):
        """Test case for finish-of-line"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.12", "3.12"),
            after_sel=("3.9", "3.9"),
            command_name="finish-of-line",
        )
    #@+node:ekr.20201130090918.54: *5* finish-of-line (2)
    def test_finish_of_line_2(self):
        """Test case for finish-of-line (2)"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.1", "3.1"),
            after_sel=("3.9", "3.9"),
            command_name="finish-of-line",
        )
    #@+node:ekr.20201130090918.55: *5* finish-of-line-extend-selection
    def test_finish_of_line_extend_selection(self):
        """Test case for finish-of-line-extend-selection"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.1", "3.1"),
            after_sel=("3.1", "3.9"),
            command_name="finish-of-line-extend-selection",
        )
    #@+node:ekr.20201130090918.57: *5* forward-char
    def test_forward_char(self):
        """Test case for forward-char"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.2", "1.2"),
            after_sel=("1.3", "1.3"),
            command_name="forward-char",
        )
    #@+node:ekr.20201130090918.58: *5* forward-char-extend-selection
    def test_forward_char_extend_selection(self):
        """Test case for forward-char-extend-selection"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.1", "1.1"),
            after_sel=("1.1", "1.2"),
            command_name="forward-char-extend-selection",
        )
    #@+node:ekr.20201130090918.59: *5* forward-end-word (end of line)
    def test_forward_end_word_end_of_line(self):
        """Test case for forward-end-word (end of line)"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.395", "1.395"),
            after_sel=("3.4", "3.4"),
            command_name="forward-end-word",
        )
    #@+node:ekr.20201130090918.60: *5* forward-end-word (start of word)
    def test_forward_end_word_start_of_word(self):
        """Test case for forward-end-word (start of word)"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.310", "1.310"),
            after_sel=("1.317", "1.317"),
            command_name="forward-end-word",
        )
    #@+node:ekr.20201130090918.61: *5* forward-end-word-extend-selection
    def test_forward_end_word_extend_selection(self):
        """Test case for forward-end-word-extend-selection"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.20", "3.20"),
            after_sel=("3.20", "3.30"),
            command_name="forward-end-word-extend-selection",
        )
    #@+node:ekr.20201130090918.62: *5* forward-paragraph
    def test_forward_paragraph(self):
        """Test case for forward-paragraph"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("9.0", "9.0"),
            after_sel=("15.0", "15.0"),
            command_name="forward-paragraph",
        )
    #@+node:ekr.20201130090918.63: *5* forward-paragraph-extend-selection
    def test_forward_paragraph_extend_selection(self):
        """Test case for forward-paragraph-extend-selection"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("10.0", "10.0"),
            after_sel=("10.0", "15.0"),
            command_name="forward-paragraph-extend-selection",
        )
    #@+node:ekr.20201130090918.64: *5* forward-sentence
    def test_forward_sentence(self):
        """Test case for forward-sentence"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.17", "3.17"),
            after_sel=("3.142", "3.142"),
            command_name="forward-sentence",
        )
    #@+node:ekr.20201130090918.65: *5* forward-sentence-extend-selection
    def test_forward_sentence_extend_selection(self):
        """Test case for forward-sentence-extend-selection"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.264", "1.264"),
            after_sel=("1.264", "1.395"),
            command_name="forward-sentence-extend-selection",
        )
    #@+node:ekr.20201130090918.66: *5* forward-word
    def test_forward_word(self):
        """Test case for forward-word"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.261", "1.261"),
            after_sel=("1.272", "1.272"),
            command_name="forward-word",
        )
    #@+node:ekr.20201130090918.67: *5* forward-word-extend-selection
    def test_forward_word_extend_selection(self):
        """Test case for forward-word-extend-selection"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.395", "1.395"),
            after_sel=("1.395", "3.4"),
            command_name="forward-word-extend-selection",
        )
    #@+node:ekr.20201130090918.68: *5* indent-relative
    def test_indent_relative(self):
        """Test case for indent-relative"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
            line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("5.0", "5.0"),
            after_sel=("5.8", "5.8"),
            command_name="indent-relative",
        )
    #@+node:ekr.20201130090918.69: *5* indent-rigidly
    def test_indent_rigidly(self):
        """Test case for indent-rigidly"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    TABline 1
    TAB    line a
    TAB        line b
    TABline c
    last line
    """.replace('TAB', '\t')
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.0", "5.0"),
            after_sel=("2.0", "5.1"),
            command_name="indent-rigidly",
        )
    #@+node:ekr.20201130090918.70: *5* indent-to-comment-column
    def test_indent_to_comment_column(self):
        """Test case for indent-to-comment-column"""
        before_b = """\
    first line
    line b
    last line
    """
        after_b = """\
    first line
        line b
    last line
    """
        self.c.editCommands.ccolumn = 4  # Set the comment column
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.0", "2.0"),
            after_sel=("2.4", "2.4"),
            command_name="indent-to-comment-column",
        )
    #@+node:ekr.20201130090918.71: *5* insert-newline
    def test_insert_newline(self):
        """Test case for insert-newline"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first li
    ne
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.8", "1.8"),
            after_sel=("2.0", "2.0"),
            command_name="insert-newline",
        )
    #@+node:ekr.20210926144000.1: *5* insert-newline-bug-2230
    def test_insert_newline_bug_2230(self):
        """Test case for insert-newline"""
        before_b = textwrap.dedent("""\
    #@@language python
    def spam():
        if 1:  # test
    # after line
    """)
        # There are 8 spaces in the line after "if 1:..."
        after_b = textwrap.dedent("""\
    #@@language python
    def spam():
        if 1:  # test

    # after line
    """)
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.18", "3.18"),
            after_sel=("4.8", "4.8"),
            command_name="insert-newline",
        )
    #@+node:ekr.20201130090918.72: *5* insert-parentheses
    def test_insert_parentheses(self):
        """Test case for insert-parentheses"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first() line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.5", "1.5"),
            after_sel=("1.6", "1.6"),
            command_name="insert-parentheses",
        )
    #@+node:ekr.20201130090918.76: *5* kill-line end-body-text
    def test_kill_line_end_body_text(self):
        """Test case for kill-line end-body-text"""
        before_b = """\
    line 1
    line 2
    line 3
    """
        after_b = """\
    line 1
    line 2
    line 3"""
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("4.1", "4.1"),
            after_sel=("3.6", "3.6"),
            command_name="kill-line",
        )
    #@+node:ekr.20201130090918.77: *5* kill-line end-line-text
    def test_kill_line_end_line_text(self):
        """Test case for kill-line end-line-text"""
        before_b = """\
    line 1
    line 2
    line 3
    """
        after_b = """\
    line 1
    line 2

    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.5", "3.5"),
            after_sel=("3.0", "3.0"),
            command_name="kill-line",
        )
    #@+node:ekr.20201130090918.79: *5* kill-line start-blank-line
    def test_kill_line_start_blank_line(self):
        """Test case for kill-line start-blank-line"""
        before_b = """\
    line 1
    line 2

    line 4
    """
        after_b = """\
    line 1
    line 2
    line 4
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.0", "3.0"),
            after_sel=("3.0", "3.0"),
            command_name="kill-line",
        )
    #@+node:ekr.20201130090918.78: *5* kill-line start-line
    def test_kill_line_start_line(self):
        """Test case for kill-line start-line"""
        before_b = """\
    line 1
    line 2
    line 3
    line 4
    """
        after_b = """\
    line 1
    line 2

    line 4
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.0", "3.0"),
            after_sel=("3.0", "3.0"),
            command_name="kill-line",
        )
    #@+node:ekr.20201130090918.73: *5* kill-paragraph
    def test_kill_paragraph(self):
        """Test case for kill-paragraph"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.

    Some 90% of all presidentially declared disasters are weather related, leading
    to around 500 deaths per year and nearly $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK, helps arm America's communities with the
    communication and safety skills needed to save lives and property– before and
    during the event. StormReady helps community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year,
    Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000
    tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly
    weather impacts every American. Communities can now rely on the National Weather
    Service’s StormReady program to help them guard against the ravages of Mother
    Nature.



    StormReady communities are better prepared to save lives from the onslaught of
    severe weather through better planning, education, and awareness. No community
    is storm proof, but StormReady can help communities save lives. Does StormReady
    make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("9.0", "9.0"),
            after_sel=("8.0", "8.0"),
            command_name="kill-paragraph",
        )
    #@+node:ekr.20201130090918.74: *5* kill-sentence
    def test_kill_sentence(self):
        """Test case for kill-sentence"""
        before_b = """\
    This is the first sentence.  This
    is the second sentence.  And
    this is the last sentence.
    """
        after_b = """\
    This is the first sentence.  And
    this is the last sentence.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.2", "2.2"),
            after_sel=("1.27", "1.27"),
            command_name="kill-sentence",
        )
    #@+node:ekr.20201130090918.82: *5* kill-to-end-of-line after last visible char
    def test_kill_to_end_of_line_after_last_visible_char(self):
        """Test case for kill-to-end-of-line after last visible char"""
        before_b = """\
    line 1
    # The next line contains two trailing blanks.
    line 3
    line 4
    """
        after_b = """\
    line 1
    # The next line contains two trailing blanks.
    line 3line 4
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.6", "3.6"),
            after_sel=("3.6", "3.6"),
            command_name="kill-to-end-of-line",
        )
    #@+node:ekr.20201130090918.80: *5* kill-to-end-of-line end-body-text
    def test_kill_to_end_of_line_end_body_text(self):
        """Test case for kill-to-end-of-line end-body-text"""
        before_b = """\
    line 1
    line 2
    line 3
    """
        after_b = """\
    line 1
    line 2
    line 3"""
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("4.1", "4.1"),
            after_sel=("3.6", "3.6"),
            command_name="kill-to-end-of-line",
        )
    #@+node:ekr.20201130090918.81: *5* kill-to-end-of-line end-line
    def test_kill_to_end_of_line_end_line(self):
        """Test case for kill-to-end-of-line end-line"""
        before_b = """\
    line 1
    line 2
    line 3
    """
        after_b = """\
    line 1
    line 2line 3
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.6", "2.6"),
            after_sel=("2.6", "2.6"),
            command_name="kill-to-end-of-line",
        )
    #@+node:ekr.20201130090918.85: *5* kill-to-end-of-line middle-line
    def test_kill_to_end_of_line_middle_line(self):
        """Test case for kill-to-end-of-line middle-line"""
        before_b = """\
    line 1
    line 2
    line 3
    """
        after_b = """\
    line 1
    li
    line 3
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.2", "2.2"),
            after_sel=("2.2", "2.2"),
            command_name="kill-to-end-of-line",
        )
    #@+node:ekr.20201130090918.84: *5* kill-to-end-of-line start-blank-line
    def test_kill_to_end_of_line_start_blank_line(self):
        """Test case for kill-to-end-of-line start-blank-line"""
        before_b = """\
    line 1
    line 2

    line 4
    """
        after_b = """\
    line 1
    line 2
    line 4
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.0", "3.0"),
            after_sel=("3.0", "3.0"),
            command_name="kill-to-end-of-line",
        )
    #@+node:ekr.20201130090918.83: *5* kill-to-end-of-line start-line
    def test_kill_to_end_of_line_start_line(self):
        """Test case for kill-to-end-of-line start-line"""
        before_b = """\
    line 1
    line 2
    line 3
    line 4
    """
        after_b = """\
    line 1
    line 2

    line 4
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.0", "3.0"),
            after_sel=("3.0", "3.0"),
            command_name="kill-to-end-of-line",
        )
    #@+node:ekr.20201130090918.75: *5* kill-word
    def test_kill_word(self):
        """Test case for kill-word"""
        before_b = """\
    This is the first sentence.  This
    is the second sentence.  And
    this is the last sentence.
    """
        after_b = """\
    This is the first sentence.  This
    is the  sentence.  And
    this is the last sentence.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.6", "2.6"),
            after_sel=("2.7", "2.7"),
            command_name="kill-word",
        )
    #@+node:ekr.20210829062149.1: *4* Commands M-R
    #@+node:ekr.20220517064432.1: *5* merge-node-with-next-node
    def test_merge_node_with_next_node(self):
        c, u = self.c, self.c.undoer
        prev_b = textwrap.dedent("""\
    def spam():
        pass
    """)
        next_b = textwrap.dedent("""\
    spam2 = spam
    """)
        result_b = textwrap.dedent("""\
    def spam():
        pass

    spam2 = spam
    """)
        self.before_p.b = prev_b
        self.after_p.b = next_b
        c.selectPosition(self.before_p)
        # Delete 'before', select 'after'
        c.doCommandByName('merge-node-with-next-node')
        self.assertEqual(c.p.h, 'after')
        self.assertEqual(c.p.b, result_b)
        self.assertFalse(c.p.next())
        # Restore 'before', select, 'before'.
        u.undo()
        self.assertEqual(c.p.h, 'before')
        self.assertEqual(c.p.b, prev_b)
        self.assertEqual(c.p.next().h, 'after')
        self.assertEqual(c.p.next().b, next_b)
        u.redo()
        self.assertEqual(c.p.h, 'after')
        self.assertEqual(c.p.b, result_b)
        self.assertFalse(c.p.next())
    #@+node:ekr.20220517064507.1: *5* merge-node-with-prev-node
    def test_merge_node_with_prev_node(self):
        c, u = self.c, self.c.undoer
        prev_b = textwrap.dedent("""\
    def spam():
        pass
    """)
        next_b = textwrap.dedent("""\
    spam2 = spam
    """)
        result_b = textwrap.dedent("""\
    def spam():
        pass

    spam2 = spam
    """)
        self.before_p.b = prev_b
        self.after_p.b = next_b
        c.selectPosition(self.after_p)
        # Delete 'after', select 'before'
        c.doCommandByName('merge-node-with-prev-node')
        self.assertEqual(c.p.h, 'before')
        self.assertEqual(c.p.b, result_b)
        self.assertFalse(c.p.next())
        # Restore 'after', select, 'after'.
        u.undo()
        self.assertEqual(c.p.h, 'after')
        self.assertEqual(c.p.b, next_b)
        self.assertEqual(c.p.back().h, 'before')
        self.assertEqual(c.p.back().b, prev_b)
        u.redo()
        self.assertEqual(c.p.h, 'before')
        self.assertEqual(c.p.b, result_b)
        self.assertFalse(c.p.next())
    #@+node:ekr.20201130090918.86: *5* move-lines-down
    def test_move_lines_down(self):
        """Test case for move-lines-down"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
    line c
        line a
            line b
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.3", "4.3"),
            after_sel=("4.3", "5.3"),
            command_name="move-lines-down",
        )
    #@+node:ekr.20201130090918.87: *5* move-lines-up
    def test_move_lines_up(self):
        """Test case for move-lines-up"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    line 1
    first line
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.2", "2.2"),
            after_sel=("1.2", "1.2"),
            command_name="move-lines-up",
        )
    #@+node:ekr.20201130090918.88: *5* move-lines-up (into docstring)
    def test_move_lines_up_into_docstring(self):
        """Test case for move-lines-up (into docstring)"""
        before_b = '''\
    #@@language python
    def test():
        """ a
        b
        c
        """
        print 1

        print 2
    '''
        after_b = '''\
    #@@language python
    def test():
        """ a
        b
        c
        print 1
        """

        print 2
    '''
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("7.1", "7.1"),
            after_sel=("6.1", "6.1"),
            command_name="move-lines-up",
        )
    #@+node:ekr.20201130090918.89: *5* move-past-close
    def test_move_past_close(self):
        """Test case for move-past-close"""
        before_b = """\
    first (line)
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first (line)
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.10", "1.10"),
            after_sel=("1.12", "1.12"),
            command_name="move-past-close",
        )
    #@+node:ekr.20201130090918.90: *5* move-past-close-extend-selection
    def test_move_past_close_extend_selection(self):
        """Test case for move-past-close-extend-selection"""
        before_b = """\
    first line
    line 1
        (line )a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        (line )a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.7", "3.7"),
            after_sel=("3.7", "3.11"),
            command_name="move-past-close-extend-selection",
        )
    #@+node:ekr.20201130090918.91: *5* newline-and-indent
    def test_newline_and_indent(self):
        """Test case for newline-and-indent"""
        before_b = textwrap.dedent("""\
    first line
    line 1
        line a
            line b
    line c
    last line
    """)
        # docstrings strip blank lines, so we can't use a docstring here!
        after_b = ''.join([
            'first line\n'
            'line 1\n'
            '    \n',  # Would be stripped in a docstring!
            '    line a\n'
            '        line b\n'
            'line c\n'
            'last line\n'
        ])
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.6", "2.6"),
            after_sel=("3.4", "3.4"),
            command_name="newline-and-indent",
            dedent=False
        )
    #@+node:ekr.20201130090918.92: *5* next-line
    def test_next_line(self):
        """Test case for next-line"""
        before_b = """\
    a

    b
    """
        after_b = """\
    a

    b
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.1", "1.1"),
            after_sel=("2.0", "2.0"),
            command_name="next-line",
        )
    #@+node:ekr.20201130090918.93: *5* previous-line
    def test_previous_line(self):
        """Test case for previous-line"""
        before_b = """\
    a

    b
    """
        after_b = """\
    a

    b
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.0", "3.0"),
            after_sel=("2.0", "2.0"),
            command_name="previous-line",
        )
    #@+node:ekr.20201130090918.94: *5* rectangle-clear
    def test_rectangle_clear(self):
        """Test case for rectangle-clear"""
        before_b = """\
    before
    aaaxxxbbb
    aaaxxxbbb
    aaaxxxbbb
    aaaxxxbbb
    after
    """
        after_b = """\
    before
    aaa   bbb
    aaa   bbb
    aaa   bbb
    aaa   bbb
    after
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.3", "5.6"),
            after_sel=("2.3", "5.6"),
            command_name="rectangle-clear",
        )
    #@+node:ekr.20201130090918.95: *5* rectangle-close
    def test_rectangle_close(self):
        """Test case for rectangle-close"""
        before_b = """\
    before
    aaa   bbb
    aaa   bbb
    aaa   bbb
    aaa   bbb
    after
    """
        after_b = """\
    before
    aaabbb
    aaabbb
    aaabbb
    aaabbb
    after
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.3", "5.6"),
            after_sel=("2.3", "5.3"),
            command_name="rectangle-close",
        )
    #@+node:ekr.20201130090918.96: *5* rectangle-delete
    def test_rectangle_delete(self):
        """Test case for rectangle-delete"""
        before_b = """\
    before
    aaaxxxbbb
    aaaxxxbbb
    aaaxxxbbb
    aaaxxxbbb
    after
    """
        after_b = """\
    before
    aaabbb
    aaabbb
    aaabbb
    aaabbb
    after
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.3", "5.6"),
            after_sel=("2.3", "5.3"),
            command_name="rectangle-delete",
        )
    #@+node:ekr.20201130090918.97: *5* rectangle-kill
    def test_rectangle_kill(self):
        """Test case for rectangle-kill"""
        before_b = """\
    before
    aaaxxxbbb
    aaaxxxbbb
    aaaxxxbbb
    aaaxxxbbb
    after
    """
        after_b = """\
    before
    aaabbb
    aaabbb
    aaabbb
    aaabbb
    after
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.3", "5.6"),
            after_sel=("5.3", "5.3"),
            command_name="rectangle-kill",
        )
    #@+node:ekr.20201130090918.98: *5* rectangle-open
    def test_rectangle_open(self):
        """Test case for rectangle-open"""
        before_b = """\
    before
    aaaxxxbbb
    aaaxxxbbb
    aaaxxxbbb
    aaaxxxbbb
    after
    """
        after_b = """\
    before
    aaa   xxxbbb
    aaa   xxxbbb
    aaa   xxxbbb
    aaa   xxxbbb
    after
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.3", "5.6"),
            after_sel=("2.3", "5.6"),
            command_name="rectangle-open",
        )
    #@+node:ekr.20201130090918.99: *5* test_rectangle-string
    def test_rectangle_string(self):
        """Test case for rectangle-string"""
        before_b = textwrap.dedent("""\
            before
            aaaxxxbbb
            aaaxxxbbb
            aaaxxxbbb
            aaaxxxbbb
            after
    """)
        after_b = textwrap.dedent("""\
            before
            aaas...sbbb
            aaas...sbbb
            aaas...sbbb
            aaas...sbbb
            after
    """)
        # A hack. The command tests for g.unitTesting!
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.3", "5.6"),
            after_sel=("2.3", "5.8"),
            command_name="rectangle-string",
        )
    #@+node:ekr.20201130090918.100: *5* test_rectangle-yank
    def test_rectangle_yank(self):
        """Test case for rectangle-yank"""
        before_b = textwrap.dedent("""\
            before
            aaaxxxbbb
            aaaxxxbbb
            aaaxxxbbb
            aaaxxxbbb
            after
        """)
        after_b = textwrap.dedent("""\
            before
            aaaY1Ybbb
            aaaY2Ybbb
            aaaY3Ybbb
            aaaY4Ybbb
            after
        """)
        # A hack. The command tests for g.unitTesting!
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.3", "5.6"),
            after_sel=("2.3", "5.6"),
            command_name="rectangle-yank",
        )

    #@+node:ekr.20201130090918.122: *5* reformat-paragraph list 1 of 5
    def test_reformat_paragraph_list_1_of_5(self):
        """Test case for reformat-paragraph list 1 of 5"""
        before_b = """\
    This paragraph leads of this test.  It is the "lead"
    paragraph.

      1. This is item
         number 1.  It is the first item in the list.

      2. This is item
         number 2.  It is the second item in the list.

      3. This is item
         number 3.  It is the third item in the list.

    This paragraph ends the test.  It is the "final"
    paragraph.
    """
        after_b = """\
    This paragraph leads of this test. It is
    the "lead" paragraph.

      1. This is item
         number 1.  It is the first item in the list.

      2. This is item
         number 2.  It is the second item in the list.

      3. This is item
         number 3.  It is the third item in the list.

    This paragraph ends the test.  It is the "final"
    paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("4.0", "4.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.123: *5* reformat-paragraph list 2 of 5
    def test_reformat_paragraph_list_2_of_5(self):
        """Test case for reformat-paragraph list 2 of 5"""
        before_b = """\
    This paragraph leads of this test. It is
    the "lead" paragraph.

      1. This is item number 1. It is the
         first item in the list.

      2. This is item
         number 2.  It is the second item in the list.

      3. This is item
         number 3.  It is the third item in the list.

    This paragraph ends the test.  It is the "final"
    paragraph.
    """
        after_b = """\
    This paragraph leads of this test. It is
    the "lead" paragraph.

      1. This is item number 1. It is the
         first item in the list.

      2. This is item
         number 2.  It is the second item in the list.

      3. This is item
         number 3.  It is the third item in the list.

    This paragraph ends the test.  It is the "final"
    paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("4.0", "4.0"),
            after_sel=("7.0", "7.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.124: *5* reformat-paragraph list 3 of 5
    def test_reformat_paragraph_list_3_of_5(self):
        """Test case for reformat-paragraph list 3 of 5"""
        before_b = """\
    This paragraph leads of this test. It is
    the "lead" paragraph.

      1. This is item number 1. It is the
         first item in the list.

      2. This is item
         number 2.  It is the second item in the list.

      3. This is item
         number 3.  It is the third item in the list.

    This paragraph ends the test.  It is the "final"
    paragraph.
    """
        after_b = """\
    This paragraph leads of this test. It is
    the "lead" paragraph.

      1. This is item number 1. It is the
         first item in the list.

      2. This is item number 2. It is the
         second item in the list.

      3. This is item
         number 3.  It is the third item in the list.

    This paragraph ends the test.  It is the "final"
    paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("7.0", "7.0"),
            after_sel=("10.0", "10.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.125: *5* reformat-paragraph list 4 of 5
    def test_reformat_paragraph_list_4_of_5(self):
        """Test case for reformat-paragraph list 4 of 5"""
        before_b = """\
    This paragraph leads of this test. It is
    the "lead" paragraph.

      1. This is item number 1. It is the
         first item in the list.

      2. This is item number 2. It is the
         second item in the list.

      3. This is item
         number 3.  It is the third item in the list.

    This paragraph ends the test.  It is the "final"
    paragraph.
    """
        after_b = """\
    This paragraph leads of this test. It is
    the "lead" paragraph.

      1. This is item number 1. It is the
         first item in the list.

      2. This is item number 2. It is the
         second item in the list.

      3. This is item number 3. It is the
         third item in the list.

    This paragraph ends the test.  It is the "final"
    paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("10.0", "10.0"),
            after_sel=("13.0", "13.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.126: *5* reformat-paragraph list 5 of 5
    def test_reformat_paragraph_list_5_of_5(self):
        """Test case for reformat-paragraph list 5 of 5"""
        before_b = """\
    This paragraph leads of this test. It is
    the "lead" paragraph.

      1. This is item number 1. It is the
         first item in the list.

      2. This is item number 2. It is the
         second item in the list.

      3. This is item number 3. It is the
         third item in the list.

    This paragraph ends the test.  It is the "final"
    paragraph.
    """
        after_b = """\
    This paragraph leads of this test. It is
    the "lead" paragraph.

      1. This is item number 1. It is the
         first item in the list.

      2. This is item number 2. It is the
         second item in the list.

      3. This is item number 3. It is the
         third item in the list.

    This paragraph ends the test. It is the
    "final" paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("13.0", "13.0"),
            after_sel=("15.1", "15.1"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.127: *5* reformat-paragraph new code 1 of 8
    def test_reformat_paragraph_new_code_1_of_8(self):
        """Test case for reformat-paragraph new code 1 of 8"""
        before_b = """\
    #@@pagewidth 40
    '''
    docstring.
    '''
    """
        after_b = """\
    #@@pagewidth 40
    '''
    docstring.
    '''
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("2.0", "2.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.128: *5* reformat-paragraph new code 2 of 8
    def test_reformat_paragraph_new_code_2_of_8(self):
        """Test case for reformat-paragraph new code 2 of 8"""
        before_b = """\
    #@@pagewidth 40
    '''
    docstring.
    '''
    """
        after_b = """\
    #@@pagewidth 40
    '''
    docstring.
    '''
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.0", "2.0"),
            after_sel=("3.0", "3.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.129: *5* reformat-paragraph new code 3 of 8
    def test_reformat_paragraph_new_code_3_of_8(self):
        """Test case for reformat-paragraph new code 3 of 8"""
        before_b = """\
    #@@pagewidth 40
    '''
    docstring.
    more docstring.
    '''
    """
        after_b = """\
    #@@pagewidth 40
    '''
    docstring. more docstring.
    '''
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.1", "4.1"),
            after_sel=("4.0", "4.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.130: *5* reformat-paragraph new code 4 of 8
    def test_reformat_paragraph_new_code_4_of_8(self):
        """Test case for reformat-paragraph new code 4 of 8"""
        before_b = """\
    - Point 1. xxxxxxxxxxxxxxxxxxxxxxxxxxxx
    Line 11.
    A. Point 2. xxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
        after_b = """\
    - Point 1. xxxxxxxxxxxxxxxxxxxxxxxxxxxx
      Line 11.
    A. Point 2. xxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("3.0", "3.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.131: *5* reformat-paragraph new code 5 of 8
    def test_reformat_paragraph_new_code_5_of_8(self):
        """Test case for reformat-paragraph new code 5 of 8"""
        before_b = """\
    A. Point 2. xxxxxxxxxxxxxxxxxxxxxxxxxxx
      Line 22.
    1. Point 3. xxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
        after_b = """\
    A. Point 2. xxxxxxxxxxxxxxxxxxxxxxxxxxx
       Line 22.
    1. Point 3. xxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "2.0"),
            after_sel=("3.0", "3.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.132: *5* reformat-paragraph new code 6 of 8
    def test_reformat_paragraph_new_code_6_of_8(self):
        """Test case for reformat-paragraph new code 6 of 8"""
        before_b = """\
    1. Point 3. xxxxxxxxxxxxxxxxxxxxxxxxxxx
    Line 32.

    2. Point 4  xxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
        after_b = """\
    1. Point 3. xxxxxxxxxxxxxxxxxxxxxxxxxxx
       Line 32.

    2. Point 4  xxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("4.0", "4.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.133: *5* reformat-paragraph new code 7 of 8
    def test_reformat_paragraph_new_code_7_of_8(self):
        """Test case for reformat-paragraph new code 7 of 8"""
        before_b = """\
    1. Point 3. xxxxxxxxxxxxxxxxxxxxxxxxxxx
       Line 32.

    2. Point 4 xxxxxxxxxxxxxxxxxxxxxxxxxxx
            Line 41.
    """
        after_b = """\
    1. Point 3. xxxxxxxxxxxxxxxxxxxxxxxxxxx
       Line 32.

    2. Point 4 xxxxxxxxxxxxxxxxxxxxxxxxxxx
            Line 41.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.11", "2.11"),
            after_sel=("3.1", "3.1"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.134: *5* reformat-paragraph new code 8 of 8
    def test_reformat_paragraph_new_code_8_of_8(self):
        """Test case for reformat-paragraph new code 8 of 8"""
        before_b = """\
    2. Point 4 xxxxxxxxxxxxxxxxxxxxxxxxxxx
            Line 41.
    """
        after_b = """\
    2. Point 4 xxxxxxxxxxxxxxxxxxxxxxxxxxx
            Line 41.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("3.0", "3.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.135: *5* reformat-paragraph paragraph 1 of 3
    def test_reformat_paragraph_paragraph_1_of_3(self):
        """Test case for reformat-paragraph paragraph 1 of 3"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?

    Last paragraph.
    """
        after_b = """\
    Americans live in the most severe
    weather-prone country on Earth. Each
    year, Americans cope with an average of
    10,000 thunderstorms, 2,500 floods,
    1,000 tornadoes, as well as an average
    of 6 deadly hurricanes. Potentially
    deadly weather impacts every American.
    Communities can now rely on the National
    Weather Service’s StormReady program to
    help them guard against the ravages of
    Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?

    Last paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("13.0", "13.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.136: *5* reformat-paragraph paragraph 2 of 3
    def test_reformat_paragraph_paragraph_2_of_3(self):
        """Test case for reformat-paragraph paragraph 2 of 3"""
        before_b = """\
    Americans live in the most severe
    weather-prone country on Earth. Each
    year, Americans cope with an average of
    10,000 thunderstorms, 2,500 floods,
    1,000 tornadoes, as well as an average
    of 6 deadly hurricanes. Potentially
    deadly weather impacts every American.
    Communities can now rely on the National
    Weather Service’s StormReady program to
    help them guard against the ravages of
    Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?

    Last paragraph.
    """
        after_b = """\
    Americans live in the most severe
    weather-prone country on Earth. Each
    year, Americans cope with an average of
    10,000 thunderstorms, 2,500 floods,
    1,000 tornadoes, as well as an average
    of 6 deadly hurricanes. Potentially
    deadly weather impacts every American.
    Communities can now rely on the National
    Weather Service’s StormReady program to
    help them guard against the ravages of
    Mother Nature.

    Some 90% of all presidentially declared
    disasters are weather related, leading
    to around 500 deaths per year and nearly
    $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK,
    helps arm America's communities with the
    communication and safety skills needed
    to save lives and property– before and
    during the event. StormReady helps
    community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?

    Last paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("13.0", "13.0"),
            after_sel=("25.0", "25.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.137: *5* reformat-paragraph paragraph 3 of 3
    def test_reformat_paragraph_paragraph_3_of_3(self):
        """Test case for reformat-paragraph paragraph 3 of 3"""
        before_b = """\
    Americans live in the most severe
    weather-prone country on Earth. Each
    year, Americans cope with an average of
    10,000 thunderstorms, 2,500 floods,
    1,000 tornadoes, as well as an average
    of 6 deadly hurricanes. Potentially
    deadly weather impacts every American.
    Communities can now rely on the National
    Weather Service’s StormReady program to
    help them guard against the ravages of
    Mother Nature.

    Some 90% of all presidentially declared
    disasters are weather related, leading
    to around 500 deaths per year and nearly
    $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK,
    helps arm America's communities with the
    communication and safety skills needed
    to save lives and property– before and
    during the event. StormReady helps
    community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?

    Last paragraph.
    """
        after_b = """\
    Americans live in the most severe
    weather-prone country on Earth. Each
    year, Americans cope with an average of
    10,000 thunderstorms, 2,500 floods,
    1,000 tornadoes, as well as an average
    of 6 deadly hurricanes. Potentially
    deadly weather impacts every American.
    Communities can now rely on the National
    Weather Service’s StormReady program to
    help them guard against the ravages of
    Mother Nature.

    Some 90% of all presidentially declared
    disasters are weather related, leading
    to around 500 deaths per year and nearly
    $14 billion in damage. StormReady, a
    program started in 1999 in Tulsa, OK,
    helps arm America's communities with the
    communication and safety skills needed
    to save lives and property– before and
    during the event. StormReady helps
    community leaders and emergency managers
    strengthen local safety programs.

    StormReady communities are better
    prepared to save lives from the
    onslaught of severe weather through
    better planning, education, and
    awareness. No community is storm proof,
    but StormReady can help communities save
    lives. Does StormReady make a
    difference?

    Last paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("25.10", "25.10"),
            after_sel=("34.0", "34.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.138: *5* reformat-paragraph simple hanging indent
    def test_reformat_paragraph_simple_hanging_indent(self):
        """Test case for reformat-paragraph simple hanging indent"""
        before_b = """\
    Honor this line that has a hanging indentation, please.  Hanging
      indentation is valuable for lists of all kinds.  But it is tricky to get right.

    Next paragraph.
    """
        after_b = """\
    Honor this line that has a hanging
      indentation, please. Hanging
      indentation is valuable for lists of
      all kinds. But it is tricky to get
      right.

    Next paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("7.0", "7.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.139: *5* reformat-paragraph simple hanging indent 2
    def test_reformat_paragraph_simple_hanging_indent_2(self):
        """Test case for reformat-paragraph simple hanging indent 2"""
        before_b = """\
    Honor this line that has
      a hanging indentation, please.  Hanging
        indentation is valuable for lists of all kinds.  But it is tricky to get right.

    Next paragraph.
    """
        after_b = """\
    Honor this line that has a hanging
      indentation, please. Hanging
      indentation is valuable for lists of
      all kinds. But it is tricky to get
      right.

    Next paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.0", "2.0"),
            after_sel=("7.0", "7.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.140: *5* reformat-paragraph simple hanging indent 3
    def test_reformat_paragraph_simple_hanging_indent_3(self):
        """Test case for reformat-paragraph simple hanging indent 3"""
        before_b = """\
    Honor this line that
      has a hanging indentation,
      please.  Hanging
       indentation is valuable
        for lists of all kinds.  But
        it is tricky to get right.

    Next Paragraph.
    """
        after_b = """\
    Honor this line that has a hanging
      indentation, please. Hanging
      indentation is valuable for lists of
      all kinds. But it is tricky to get
      right.

    Next Paragraph.
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "1.0"),
            after_sel=("7.0", "7.0"),
            command_name="reformat-paragraph",
            directives="@language plain\n@pagewidth 40\n@tabwidth 8",
        )
    #@+node:ekr.20201130090918.101: *5* remove-blank-lines
    def test_remove_blank_lines(self):
        """Test case for remove-blank-lines"""
        before_b = """\
    first line

    line 1
        line a
            line b

    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "9.0"),
            after_sel=("1.0", "6.9"),
            command_name="remove-blank-lines",
        )
    #@+node:ekr.20201130090918.102: *5* remove-space-from-lines
    def test_remove_space_from_lines(self):
        """Test case for remove-space-from-lines"""
        before_b = """\
    first line

    line 1
        line a
            line b

    line c
    last line
    """
        after_b = """\
    first line

    line 1
       line a
           line b

    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "9.0"),
            after_sel=("1.0", "9.0"),
            command_name="remove-space-from-lines",
        )
    #@+node:ekr.20201130090918.103: *5* remove-tab-from-lines
    def test_remove_tab_from_lines(self):
        """Test case for remove-tab-from-lines"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
    line a
        line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "7.0"),
            after_sel=("1.0", "7.0"),
            command_name="remove-tab-from-lines",
        )
    #@+node:ekr.20201130090918.104: *5* reverse-region
    def test_reverse_region(self):
        """Test case for reverse-region"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\

    last line
    line c
            line b
        line a
    line 1
    first line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "7.0"),
            after_sel=("7.10", "7.10"),
            command_name="reverse-region",
        )
    #@+node:ekr.20201130090918.105: *5* reverse-sort-lines
    def test_reverse_sort_lines(self):
        """Test case for reverse-sort-lines"""
        before_b = """\
    a
    d
    e
    z
    x
    """
        after_b = """\
    z
    x
    e
    d
    a
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "5.1"),
            after_sel=("1.0", "5.1"),
            command_name="reverse-sort-lines",
        )
    #@+node:ekr.20201130090918.106: *5* reverse-sort-lines-ignoring-case
    def test_reverse_sort_lines_ignoring_case(self):
        """Test case for reverse-sort-lines-ignoring-case"""
        before_b = """\
    c
    A
    z
    X
    Y
    b
    """
        after_b = """\
    z
    Y
    X
    c
    b
    A
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "6.1"),
            after_sel=("1.0", "6.1"),
            command_name="reverse-sort-lines-ignoring-case",
        )
    #@+node:ekr.20210829062731.1: *4* Commands S-Z
    #@+node:ekr.20201130090918.107: *5* sort-columns
    def test_sort_columns(self):
        """Test case for sort-columns"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
            line b
        line a
    first line
    last line
    line 1
    line c
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "6.2"),
            after_sel=("1.0", "7.0"),
            command_name="sort-columns",
        )
    #@+node:ekr.20201130090918.108: *5* sort-lines
    def test_sort_lines(self):
        """Test case for sort-lines"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
            line b
        line a
    line 1
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.0", "5.6"),
            after_sel=("2.0", "5.6"),
            command_name="sort-lines",
        )
    #@+node:ekr.20201130090918.109: *5* sort-lines-ignoring-case
    def test_sort_lines_ignoring_case(self):
        """Test case for sort-lines-ignoring-case"""
        before_b = """\
    x
    z
    A
    c
    B
    """
        after_b = """\
    A
    B
    c
    x
    z
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "5.1"),
            after_sel=("1.0", "5.1"),
            command_name="sort-lines-ignoring-case",
        )
    #@+node:ekr.20201130090918.110: *5* split-line
    def test_split_line(self):
        """Test case for split-line"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first
     line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.5", "1.5"),
            after_sel=("2.0", "2.0"),
            command_name="split-line",
        )
    #@+node:ekr.20201130090918.111: *5* start-of-line
    def test_start_of_line(self):
        """Test case for start-of-line"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.10", "3.10"),
            after_sel=("3.4", "3.4"),
            command_name="start-of-line",
        )
    #@+node:ekr.20201130090918.112: *5* start-of-line (2)
    def test_start_of_line_2(self):
        """Test case for start-of-line (2)"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.1", "3.1"),
            after_sel=("3.4", "3.4"),
            command_name="start-of-line",
        )
    #@+node:ekr.20201130090918.113: *5* start-of-line-extend-selection
    def test_start_of_line_extend_selection(self):
        """Test case for start-of-line-extend-selection"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.10", "3.10"),
            after_sel=("3.4", "3.10"),
            command_name="start-of-line-extend-selection",
        )
    #@+node:ekr.20201130090918.114: *5* start-of-line-extend-selection (2)
    def test_start_of_line_extend_selection_2(self):
        """Test case for start-of-line-extend-selection (2)"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.1", "3.1"),
            after_sel=("3.1", "3.4"),
            command_name="start-of-line-extend-selection",
        )
    #@+node:ekr.20201130090918.115: *5* tabify
    def test_tabify(self):
        """Test case for tabify"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
    TABline a
    TABTABline b
    line c
    last line
    """.replace('TAB', '\t')
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "7.0"),
            after_sel=("7.0", "7.0"),
            command_name="tabify",
        )
    #@+node:ekr.20201130090918.116: *5* transpose-chars
    def test_transpose_chars(self):
        """Test case for transpose-chars"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    frist line
    line 1
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.2", "1.2"),
            after_sel=("1.2", "1.2"),
            command_name="transpose-chars",
        )
    #@+node:ekr.20201130090918.117: *5* transpose-lines
    def test_transpose_lines(self):
        """Test case for transpose-lines"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    line 1
    first line
        line a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.2", "2.2"),
            after_sel=("2.10", "2.10"),
            command_name="transpose-lines",
        )
    #@+node:ekr.20201130090918.118: *5* transpose-words
    def test_transpose_words(self):
        """Test case for transpose-words"""
        before_b = """\
    first line
    before bar2 += foo after
    last line
    """
        after_b = """\
    first line
    before foo += bar2 after
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("2.9", "2.9"),
            after_sel=("2.11", "2.11"),
            command_name="transpose-words",
        )
    #@+node:ekr.20201130090918.119: *5* untabify
    def test_untabify(self):
        """Test case for untabify"""
        before_b = """\
    first line
    line 1
    TABline a
    TABTABline b
    line c
    last line
    """.replace('TAB', '\t')
        after_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """.replace('TAB', '\t')
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("1.0", "7.0"),
            after_sel=("7.0", "7.0"),
            command_name="untabify",
        )
    #@+node:ekr.20201130090918.120: *5* upcase-region
    def test_upcase_region(self):
        """Test case for upcase-region"""
        before_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    Some 90% of all presidentially declared disasters are weather related, leading to around 500 deaths per year and nearly $14 billion in damage. StormReady, a program started in 1999 in Tulsa, OK, helps arm America's communities with the communication and safety skills needed to save lives and property– before and during the event. StormReady helps community leaders and emergency managers strengthen local safety programs.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        after_b = """\
    Americans live in the most severe weather-prone country on Earth. Each year, Americans cope with an average of 10,000 thunderstorms, 2,500 floods, 1,000 tornadoes, as well as an average of 6 deadly hurricanes. Potentially deadly weather impacts every American. Communities can now rely on the National Weather Service’s StormReady program to help them guard against the ravages of Mother Nature.

    SOME 90% OF ALL PRESIDENTIALLY DECLARED DISASTERS ARE WEATHER RELATED, LEADING TO AROUND 500 DEATHS PER YEAR AND NEARLY $14 BILLION IN DAMAGE. STORMREADY, A PROGRAM STARTED IN 1999 IN TULSA, OK, HELPS ARM AMERICA'S COMMUNITIES WITH THE COMMUNICATION AND SAFETY SKILLS NEEDED TO SAVE LIVES AND PROPERTY– BEFORE AND DURING THE EVENT. STORMREADY HELPS COMMUNITY LEADERS AND EMERGENCY MANAGERS STRENGTHEN LOCAL SAFETY PROGRAMS.

    StormReady communities are better prepared to save lives from the onslaught of severe weather through better planning, education, and awareness. No community is storm proof, but StormReady can help communities save lives. Does StormReady make a difference?
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.0", "4.0"),
            after_sel=("3.0", "4.0"),
            command_name="upcase-region",
        )
    #@+node:ekr.20201130090918.121: *5* upcase-word
    def test_upcase_word(self):
        """Test case for upcase-word"""
        before_b = """\
    first line
    line 1
        line a
            line b
    line c
    last line
    """
        after_b = """\
    first line
    line 1
        LINE a
            line b
    line c
    last line
    """
        self.run_test(
            before_b=before_b,
            after_b=after_b,
            before_sel=("3.7", "3.7"),
            after_sel=("3.7", "3.7"),
            command_name="upcase-word",
        )
    #@+node:ekr.20210905064816.1: *3* TestEditCommands: Others
    #@+node:ekr.20210905064816.2: *4* TestEditCommands.test_abbrevCommands_next_place
    def test_abbrevCommands_next_place(self):
        c = self.c
        ac = c.abbrevCommands
        assert ac
        c.abbrev_place_start = '<|'
        c.abbrev_place_end = '|>'
        s = '123<| sub |>456'
        new_s, i, j = ac.next_place(s, offset=0)
        assert new_s == s.replace('<|', '').replace('|>', '')
    #@+node:ekr.20210905064816.3: *4* TestEditCommands.test_addAbbrevHelper
    def test_addAbbrevHelper(self):
        c = self.c
        f = c.abbrevCommands.addAbbrevHelper
        d = c.abbrevCommands.abbrevs

        # New in Leo 4.10: whitespace (blank,tab,newline) *is* significant in definitions.
        table = (
            ('ut1', 'ut1=aa', 'aa'),
            # ('ut2','ut2 =bb','bb'),
            ('ut3', 'ut3=cc=dd', 'cc=dd'),
            ('ut4', 'ut4= ee', ' ee'),
            ('ut5', 'ut5= ff = gg', ' ff = gg'),
            ('ut6', 'ut6= hh==ii', ' hh==ii'),
            ('ut7', 'ut7=j=k', 'j=k'),
            ('ut8', 'ut8=l==m', 'l==m'),
            ('@ut1', '@ut1=@a', '@a'),
        )
        for name, s, expected in table:
            for s2, kind in ((s, '(no nl)'), (s + '\n', '(nl)')):
                f(s2, tag='unit-test')
                result, tag = d.get(name, (None, None),)
                self.assertEqual(result, expected, msg=kind)
    #@+node:ekr.20210905064816.4: *4* TestEditCommands.test_capitalizeHelper
    def test_capitalizeHelper(self):
        c, w = self.c, self.c.frame.body.wrapper
        w.setAllText('# TARGETWORD\n')
        table = (
            ('cap', 'Targetword'),
            ('low', 'targetword'),
            ('up', 'TARGETWORD'),
        )
        for (which, result) in table:
            w.setInsertPoint(5)  # Must be inside the target.
            c.editCommands.capitalizeHelper(event=None, which=which, undoType='X')
            s = w.getAllText()
            word = s[2:12]
            self.assertEqual(word, result, msg=which)
            i = w.getInsertPoint()
            self.assertEqual(i, 5, msg=which)
    #@+node:ekr.20210905064816.16: *4* TestEditCommands.test_delete_key_sticks_in_body
    def test_delete_key_sticks_in_body(self):
        c = self.c
        w = c.frame.body.wrapper
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.selectPosition(p)
        s = 'ABC'
        c.setBodyString(p, s)
        c.bodyWantsFocus()
        w.setInsertPoint(2)
        c.outerUpdate()  # This fixed the problem.
        c.doCommandByName('delete-char')
        self.assertEqual(p.b, s[:-1])
        c.selectPosition(p.threadBack())
        c.selectPosition(p)
        self.assertEqual(p.b, s[:-1])
    #@+node:ekr.20210905064816.17: *4* TestEditCommands.test_delete_key_sticks_in_headline
    def test_delete_key_sticks_in_headline(self):
        c = self.c
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.selectPosition(p)
        c.redraw(p)  # To make node visible
        c.frame.tree.editLabel(p)
        w = c.edit_widget(p)
        try:
            assert w
            end = w.getLastIndex()
            w.setSelectionRange(end, end)
        finally:
            if 1:
                c.setHeadString(p, h)  # Essential
                c.redraw(p)
    #@+node:ekr.20210905064816.5: *4* TestEditCommands.test_dynamicExpandHelper
    def test_dynamicExpandHelper(self):
        c = self.c
        # A totally wimpy test.
        # And it somehow prints a newline to the console.
        if 0:
            c.abbrevCommands.dynamicExpandHelper(event=None, prefix='', aList=[], w=None)
    #@+node:ekr.20210905064816.6: *4* TestEditCommands.test_extendHelper
    def test_extendHelper(self):
        c = self.c
        ec = c.editCommands
        w = c.frame.body.wrapper
        for i, j, python in (
            # ('1.0','4.5',False),
            (5, 50, True),
        ):
            extend = True
            ec.moveSpot = None  # It's hard to init this properly.
            ec.extendHelper(w, extend, j)
            i2, j2 = w.getSelectionRange()
    #@+node:ekr.20210905064816.7: *4* TestEditCommands.test_findWord
    def test_findWord(self):
        c = self.c
        e, k, w = c.editCommands, c.k, c.frame.body.wrapper
        w.setAllText('start\ntargetWord\n')
        w.setInsertPoint(0)
        k.arg = 't'  # 'targetWord'
        e.w = w
        e.oneLineFlag = False
        e.findWord1(event=None)
        i, j = w.getSelectionRange()
        self.assertEqual(i, 6)
    #@+node:ekr.20210905064816.8: *4* TestEditCommands.test_findWordInLine
    def test_findWordInLine(self):
        c = self.c
        e, k, w = c.editCommands, c.k, c.frame.body.wrapper
        w.setAllText('abc\ntargetWord\n')
        k.arg = 't'  # 'targetWord'
        w.setInsertPoint(0)
        e.w = w
        e.oneLineFlag = False
        e.findWord1(event=None)
        i, j = w.getSelectionRange()
        self.assertEqual(i, 4)
    #@+node:ekr.20210905064816.9: *4* TestEditCommands.test_helpForMinibuffer
    def test_helpForMinibuffer(self):
        c = self.c
        c.helpCommands.helpForMinibuffer()
    #@+node:ekr.20210914154830.1: *4* TestEditCommands.test_helpForPython
    def test_helpForPthon(self):
        c, k = self.c, self.c.k
        k.arg = 'os'
        s = c.helpCommands.pythonHelp1(event=None)
        self.assertTrue('Help on module os' in s)
    #@+node:ekr.20210905064816.19: *4* TestEditCommands.test_insert_node_before_node_can_be_undone_and_redone
    def test_insert_node_before_node_can_be_undone_and_redone(self):
        c = self.c
        u = c.undoer
        assert u
        # pylint: disable=no-member
        c.insertHeadlineBefore()
        self.assertEqual(u.undoMenuLabel, 'Undo Insert Node Before')
        c.undoer.undo()
        self.assertEqual(u.redoMenuLabel, 'Redo Insert Node Before')
    #@+node:ekr.20210905064816.18: *4* TestEditCommands.test_insert_node_can_be_undone_and_redone
    def test_insert_node_can_be_undone_and_redone(self):
        c = self.c
        u = c.undoer
        assert u
        # pylint: disable=no-member
        c.insertHeadline()
        self.assertEqual(u.undoMenuLabel, 'Undo Insert Node')
        c.undoer.undo()
        self.assertEqual(u.redoMenuLabel, 'Redo Insert Node')
    #@+node:ekr.20210905064816.20: *4* TestEditCommands.test_inserting_a_new_node_draws_the_screen_exactly_once
    def test_inserting_a_new_node_draws_the_screen_exactly_once(self):
        c = self.c
        n = c.frame.tree.redrawCount
        # pylint: disable=no-member
        c.insertHeadline()
        c.outerUpdate()  # Not actually needed, but should not matter.
        n2 = c.frame.tree.redrawCount
        self.assertEqual(n2, n + 1)

    #@+node:ekr.20210905064816.15: *4* TestEditCommands.test_most_toggle_commands
    def test_most_toggle_commands(self):
        c, k = self.c, self.c.k
        ed = c.editCommands
        # These don't set ivars
            # 'toggle-active-pane'),
            # 'toggle-angle-brackets',
            # 'toggle-input-state'),
            # 'toggle-mini-buffer'),
            # 'toggle-split-direction'),
        table = [
            (k, 'abbrevOn', 'toggle-abbrev-mode'),
            (ed, 'extendMode', 'toggle-extend-mode'),
        ]
        for obj, ivar, command in table:
            val1 = getattr(obj, ivar)
            k.simulateCommand(command)
            val2 = getattr(obj, ivar)
            self.assertEqual(val2, not val1, msg=command)
            k.simulateCommand(command)
            val3 = getattr(obj, ivar)
            self.assertEqual(val3, val1, msg=command)
    #@+node:ekr.20210905064816.10: *4* TestEditCommands.test_moveToHelper
    def test_moveToHelper(self):
        c = self.c
        ec = c.editCommands
        w = c.frame.body.wrapper
        for i, j, python in (
            #('1.0','4.5',False),
            (5, 50, True),
        ):
            event = None
            extend = True
            ec.moveSpot = None
            w.setInsertPoint(i)
            ec.moveToHelper(event, j, extend)
            i2, j2 = w.getSelectionRange()
            self.assertEqual(i, i2)
            self.assertEqual(j, j2)
            w.setSelectionRange(0, 0, insert=None)
    #@+node:ekr.20210905064816.11: *4* TestEditCommands.test_moveUpOrDownHelper
    def test_moveUpOrDownHelper(self):
        c = self.c
        ec = c.editCommands
        w = c.frame.body.wrapper

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        table = (
            ('5.8', '4.8', 'up'),
            ('5.8', '6.8', 'down'),
        )
        for i, result, direction in table:
            w.setInsertPoint(toInt(i))
            ec.moveUpOrDownHelper(event=None, direction=direction, extend=False)
            w.getSelectionRange()
    #@+node:ekr.20210905064816.21: *4* TestEditCommands.test_paste_and_undo_in_headline__at_end
    def test_paste_and_undo_in_headline__at_end(self):
        c, k = self.c, self.c.k
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.selectPosition(p)
        c.frame.tree.editLabel(p)
        w = c.edit_widget(p)
        assert w
        end = w.getLastIndex()
        w.setSelectionRange(end, end)
        paste = 'ABC'
        g.app.gui.replaceClipboardWith(paste)
        w.setSelectionRange(end, end)
        c.frame.pasteText(event=g.Bunch(widget=w))
        g.app.gui.event_generate(c, '\n', 'Return', w)
        self.assertEqual(p.h, h + paste)
        k.manufactureKeyPressForCommandName(w, 'undo')
        self.assertEqual(p.h, h)
    #@+node:ekr.20210905064816.22: *4* TestEditCommands.test_paste_and_undo_in_headline__with_selection
    def test_paste_and_undo_in_headline__with_selection(self):
        c, k = self.c, self.c.k
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.selectPosition(p)
        c.frame.tree.editLabel(p)
        w = c.edit_widget(p)
        assert w
        paste = 'ABC'
        g.app.gui.replaceClipboardWith(paste)
        w.setSelectionRange(1, 2)
        c.frame.pasteText(event=g.Bunch(widget=w))
        g.app.gui.event_generate(c, '\n', 'Return', w)
        self.assertEqual(p.h, h[0] + paste + h[2:])
        k.manufactureKeyPressForCommandName(w, 'undo')
        self.assertEqual(p.h, h)
    #@+node:ekr.20210905064816.23: *4* TestEditCommands.test_paste_at_end_of_headline
    def test_paste_at_end_of_headline(self):
        c = self.c
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.selectPosition(p)
        c.frame.tree.editLabel(p)
        w = c.edit_widget(p)
        assert w
        end = w.getLastIndex()
        g.app.gui.set_focus(c, w)
        paste = 'ABC'
        g.app.gui.replaceClipboardWith(paste)
        g.app.gui.set_focus(c, w)
        w.setSelectionRange(end, end)
        c.frame.pasteText(event=g.Bunch(widget=w))
        g.app.gui.event_generate(c, '\n', 'Return', w)
        self.assertEqual(p.h, h + paste)
    #@+node:ekr.20210905064816.24: *4* TestEditCommands.test_paste_from_menu_into_headline_sticks
    def test_paste_from_menu_into_headline_sticks(self):
        c = self.c
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.selectPosition(p)
        c.selectPosition(p)
        c.frame.tree.editLabel(p)
        w = c.edit_widget(p)
        end = w.getLastIndex()
        w.setSelectionRange(end, end, insert=end)
        paste = 'ABC'
        g.app.gui.replaceClipboardWith(paste)
        event = g.app.gui.create_key_event(c, w=w)
        c.frame.pasteText(event)
        # Move around and and make sure it doesn't change.
        try:
            # g.trace('before select',w,w.getAllText())
            c.selectPosition(p.threadBack())
            self.assertEqual(p.h, h + paste)
            c.selectPosition(p)
            self.assertEqual(p.h, h + paste)
        finally:
            if 1:
                c.setHeadString(p, h)  # Essential
                c.redraw(p)
    #@+node:ekr.20210905064816.25: *4* TestEditCommands.test_return_ends_editing_of_headline
    def test_return_ends_editing_of_headline(self):
        c = self.c
        h = '@test return ends editing of headline'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.selectPosition(p)
        c.redraw(p)  # To make node visible
        c.frame.tree.editLabel(p)
        w = c.edit_widget(p)
        wName = g.app.gui.widget_name(w)
        assert wName.startswith('head'), 'w.name:%s' % wName
        g.app.gui.event_generate(c, '\n', 'Return', w)
        c.outerUpdate()
        assert w != c.get_focus(), 'oops2: focus in headline'
    #@+node:ekr.20210905064816.12: *4* TestEditCommands.test_scrollHelper
    def test_scrollHelper(self):
        c = self.c
        ec = c.editCommands
        w = c.frame.body.wrapper

        for direction in ('up', 'down'):
            for distance in ('line', 'page', 'half-page'):
                event = g.app.gui.create_key_event(c, w=w)
                ec.scrollHelper(event, direction, distance)
    #@+node:ekr.20210905064816.26: *4* TestEditCommands.test_selecting_new_node_retains_paste_in_headline
    def test_selecting_new_node_retains_paste_in_headline(self):
        c, k = self.c, self.c.k
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.selectPosition(p)
        c.redraw(p)  # To make node visible
        c.frame.tree.editLabel(p)
        w = c.edit_widget(p)
        end = w.getLastIndex()
        w.setSelectionRange(end, end)
        paste = 'ABC'
        g.app.gui.replaceClipboardWith(paste)
        w.setSelectionRange(end, end)
        k.manufactureKeyPressForCommandName(w, 'paste-text')
        c.selectPosition(p.visBack(c))
        self.assertEqual(p.h, h + paste)
        c.undoer.undo()
        self.assertEqual(p.h, h)
    #@+node:ekr.20210905064816.27: *4* TestEditCommands.test_selecting_new_node_retains_typing_in_headline
    def test_selecting_new_node_retains_typing_in_headline(self):
        c, k = self.c, self.c.k
        k.defaultUnboundKeyAction = 'insert'
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.selectPosition(p)
        c.redraw(p)  # Required
        c.frame.tree.editLabel(p)
        w = c.edit_widget(p)
        end = w.getLastIndex()
        w.setSelectionRange(end, end)
        # char, shortcut.
        g.app.gui.event_generate(c, 'X', 'Shift+X', w)
        g.app.gui.event_generate(c, 'Y', 'Shift+Y', w)
        g.app.gui.event_generate(c, 'Z', 'Shift+Z', w)
        g.app.gui.event_generate(c, '\n', 'Return', w)
        expected = h + 'XYZ'
        self.assertEqual(p.h, expected)
        k.manufactureKeyPressForCommandName(w, 'undo')
        self.assertEqual(p.h, h)
    #@+node:ekr.20210905064816.13: *4* TestEditCommands.test_setMoveCol
    def test_setMoveCol(self):
        c = self.c
        ec, w = c.editCommands, c.frame.body.wrapper
        table = (
            (0, 0),
            (5, 5),
        )
        w.setAllText('1234567890')
        for spot, result in table:
            ec.setMoveCol(w, spot)
            self.assertEqual(ec.moveSpot, result)
            self.assertEqual(ec.moveCol, result)
    #@+node:ekr.20210905064816.14: *4* TestEditCommands.test_toggle_extend_mode
    def test_toggle_extend_mode(self):
        c = self.c
        # backward-find-character and find-character
        # can't be tested this way because they prompt for input.
        #@+<< define table >>
        #@+node:ekr.20210905065002.1: *5* << define table >>
        # Cursor movement commands affected by extend mode.
        # The x-extend-selection commands are not so affected.
        table = (
            'back-to-indentation',
            'back-to-home',
            'back-char',
            'back-page',
            'back-paragraph',
            'back-sentence',
            'back-word',
            'beginning-of-buffer',
            'beginning-of-line',
            'end-of-buffer',
            'end-of-line',
            'forward-char',
            'forward-page',
            'forward-paragraph',
            'forward-sentence',
            'forward-end-word',
            'forward-word',
            'move-past-close',
            'next-line',
            'previous-line',
        )
        #@-<< define table >>
        w = c.frame.body.wrapper
        s = textwrap.dedent("""\
            Paragraph 1.
                line 2.

            Paragraph 2.
            line 2, paragraph 2
    """)
        w.setAllText(s)
        child = c.rootPosition().insertAfter()
        c.selectPosition(child)
        for commandName in table:
            # Put the cursor in the middle of the middle line
            # so all cursor moves will actually do something.
            w.setInsertPoint(15)
            c.editCommands.extendMode = True
            c.keyHandler.simulateCommand(commandName)
            # i, j = w.getSelectionRange()
            # self.assertNotEqual(i, j, msg=commandName)
    #@+node:ekr.20210905064816.28: *4* TestEditCommands.test_typing_and_undo_in_headline_at_end
    def test_typing_and_undo_in_headline_at_end(self):
        c, k = self.c, self.c.k
        k.defaultUnboundKeyAction = 'insert'
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.redrawAndEdit(p)  # Required
        w = c.edit_widget(p)
        assert w
        end = w.getLastIndex()
        wName = g.app.gui.widget_name(w)
        self.assertTrue(wName.startswith('head'))
        w.setSelectionRange(end, end)
        g.app.gui.event_generate(c, 'X', 'Shift+X', w)
        g.app.gui.event_generate(c, 'Y', 'Shift+Y', w)
        g.app.gui.event_generate(c, 'Z', 'Shift+Z', w)
        g.app.gui.event_generate(c, '\n', 'Return', w)
        self.assertEqual(p.h, h + 'XYZ')
        self.assertEqual(c.undoer.undoMenuLabel, 'Undo Typing')
        k.manufactureKeyPressForCommandName(w, 'undo')
        self.assertEqual(c.undoer.redoMenuLabel, 'Redo Typing')
        self.assertEqual(p.h, h)
    #@+node:ekr.20210905064816.29: *4* TestEditCommands.test_typing_in_non_empty_body_text_does_not_redraw_the_screen
    def test_typing_in_non_empty_body_text_does_not_redraw_the_screen(self):
        c = self.c
        w = c.frame.body.wrapper
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.setBodyString(p, 'a')
        p.v.iconVal = p.computeIcon()  # To suppress redraw!
        c.redraw(p)  # To make node visible
        c.bodyWantsFocus()
        n = c.frame.tree.redrawCount
        g.app.gui.event_generate(c, 'a', 'a', w)
        n2 = c.frame.tree.redrawCount
        self.assertEqual(n2, n)

    #@+node:ekr.20210905064816.30: *4* TestEditCommands.test_undoing_insert_node_restores_previous_node_s_body_text
    def test_undoing_insert_node_restores_previous_node_s_body_text(self):
        c = self.c
        h = 'Test headline abc'
        p = c.rootPosition().insertAfter()
        p.h = h
        c.selectPosition(p)
        body = 'This is a test'
        c.setBodyString(p, body)
        # pylint: disable=no-member
        self.assertEqual(p.b, body)
        c.insertHeadline()
        c.undoer.undo()
        self.assertEqual(p.b, body)
    #@-others
#@-others
#@-leo
