#!/usr/bin/python
# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20141010141310.18627: * @file ../external/PythonTidy.py
#@@first
#@@first
# PythonTidy.py. Started 2006 Oct 27 . ccr
# pylint: disable=non-parent-init-called
#@+<< docstring >>
#@+node:ekr.20141010141310.19068: ** << docstring >> PythonTidy 1.23
'''PythonTidy.py cleans up, regularizes, and reformats the text of
Python scripts.

===========================================
Copyright © 2006 Charles Curtis Rhode
===========================================

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301
USA.

===========================================
Charles Curtis Rhode,
1518 N 3rd, Sheboygan, WI 53081
mailto:CRhode@LacusVeris.com?subject=PythonTidy
===========================================

This script reads Python code from standard input and writes a revised
version to standard output.

Alternatively, it may be invoked with file names as arguments:

o python PythonTidy.py input output

Suffice it to say that *input* defaults to \'-\', the standard input,
and *output* defaults to \'-\', the standard output.

It means to encapsulate the wisdom revealed in:

o Rossum, Guido van, and Barry Warsaw. "PEP 8: Style Guide for Python
Code." 23 Mar. 2006. Python.org. 28 Nov. 2006
<http://www.python.org/dev/peps/pep-0008/>.

Python scripts are usually so good looking that no beautification is
required.  However, from time to time, it may be necessary to alter
the style to conform to changing standards.  This script converts
programs in a consistent way.  It abstracts the pretty presentation of
the symbolic code from the humdrum[1] process of writing it and
getting it to work.

This script assumes that the input Python code is well-formed and
works to begin with.  It doesn\'t check.  If all goes well, the output
Python code will work, too.  Of course, you are advised to test it
fully to be sure.

This script should be run only by python.2.5 (and perhaps higher) on
scripts written for that version (and perhaps lower) because of its
limited knowledge of and expectations for the abstract syntax tree
node classes returned by the *compiler* module.  It wouldn\'t hurt
much to try it from (and on) other versions, though, and it might
actually work.

Search this script for "Python Version Dependency."

Most of the Python 2.5 test suite passes through PythonTidy.py
unimpaired.  I ran the Python regression tests for 2.5.2 which is the
version supported by Debian 5.0 "Lenny."

On my system these tests fail before tidying:

o test_imageop
o test_pyclbr
o test_sys

282 tests succeed after tidying with the default PythonTidy global
settings, but these tests fail:

*test_grammar* exposes bug 6978 in the *compiler* module.  Tuples are
immutable and hashable and thus suitable as dict indices.  Whereas a
singleton tuple literal (x,) is valid as an index, the *compiler*
module parses it as x when it appears.

*test_dis* compares "disassembled" Python byte code to what is
expected.  While byte code for a tidied script should be functionally
equivalent to the untidied version, it will not necessarily be
identical.

*test_trace* compares the line numbers in a functional trace of a
running script with those expected.  A statement in a tidied script
will generally have a line number slightly different from the same
statement in the untidied version.

*test_doctest* is an extensive suite of tests of the *doctest* module,
which itself is used to document test code within doc strings and at
need to compare instant results against those expected.  One of the
tests in *test_doctest* appears to require line numbers consistent
with expectations, but tidied scripts generally violate such
conditions as explained above.

The more esoteric capabilities of PythonTidy.py had to be turned off
to avoid corrupting the test-suite code.  In practice, you\'ll want to
run with PERSONAL = True (See, below.) to use all the functionality,
and of course you\'ll have the good taste to find and patch all the
glitches it introduces.

[1] "Humdrum: A low cart with three wheels, drawn by one horse." The
Collaborative International Dictionary of English v.0.48.

'''
#@-<< docstring >>
from __future__ import division
VERSION = '1.23.1'
    # EKR: based on version 1.23, 2012 May 23
    # http://lacusveris.com/PythonTidy/PythonTidy-1.23.python
    # http://bugs.python.org/issue22616
DEBUG = False
PERSONAL = False
is_leo = True # Switch to suppress features not appropriate for Leo.
#@+<< imports >>
#@+node:ekr.20141010141310.19071: ** << imports >>
import leo.core.leoGlobals as g

import sys
import os
import codecs
# import StringIO
import re
import textwrap
if DEBUG:
    import token
    import doctest
import tokenize
import compiler
#@-<< imports >>
#@+<< version history >>
#@+node:ekr.20141010141310.19072: ** << version history >>
#@@nocolor-node
#@+at
# 
# 2014/10/10 EKR: Suppress features not appropriate for Leo:
# - Added is_leo constant and is_module argument to tidy_up.
# - Suppress shebang and encoding lines if is_module is False.
# - Suppress extra spacing between classes & functions.
# 
# 2014/10/10 EKR: Leo-related tweaks:
# - Added leo_c argument to tidy_up.
# - Added set_args helper, called only when c is not None.
# - NodeStr.set_as_str calls g.toEncodedString when is_leo is True.
# 
# 2014/10/10 EKR: Initial Leonized version.
# - Removed all pylint complaints.
#     - Removed duplicate keys in dictionaries.
#     - Added top-level definitions of COMMENTS, INPUT, NAME_SPACE, OUTPUT.
# - Alphabetized functions.
# - Created main function.  Not used by Leo.
# - Removed all those useless timestamps.
# - Removed unpythonic ZERO, SPACE, NULL, NA and APOST constants.
# 
# 2012 May 23 . v1.23 . ccr . Fix reference to undefined variable and
#             .       .     . elide trailing spaces for Sergey Satskiy.
#             .       .     . Don't use COL_LIMIT global for initial
#             .       .     . values.  That makes the code look as though
#             .       .     . it can't be changed later.
# 2012 Mar 04 . v1.22 . ccr . For Sakae Kobayashi: Fixed wrong default
#                     .     . for OVERRIDE_NEWLINE.
# 2010 Sep 08 . v1.21 . ccr . For Nikolai Prokoschenko:
# 
# o When double spacing is prescribed by PEP 8, do it before
# leading comments.
# 
# o Per Pep 8, double space around top-level classes only.
# 
# o Don't split index values from keys before colon.
# 
# o Preserve spelling of words in long strings containing special
# characters.
# 
# o Optionally, bring closing brackets, braces, and parens of split
# series back left to the margin of the enclosing statement.  See
# JAVA_STYLE_LIST_DEDENT.
# 
# 2010 Mar 10 . v1.20 . ccr . For Kuang-che Wu:
# 
# o Optionally preserve unassigned constants so that code to be tidied
# may contain blocks of commented-out lines that have been no-op'ed
# with leading and trailing triple quotes.  Python scripts may declare
# constants without assigning them to a variables, but PythonTidy
# considers this wasteful and normally elides them.
# 
# o Generalize an earlier exception made for PythonDoc sentinels so
# that the COMMENT_PREFIX is not inserted before any comments that
# start with doubled number-signs.
# 
# o Optionally omit parentheses around tuples, which are superfluous
# after all.  Normal PythonTidy behavior will be still to include them
# as a sort of tuple display analogous to list displays, dict
# displays, and yet-to-come set displays.
# 
# o Kuang-che Wu has provided code that removes superfluous parens in
# complex algebraic and logical expressions, which PythonTidy used to
# interpolate to make operator precedence explicit.  From now on
# PythonTidy will rely upon default operator precedence and insert
# parens only to enforce order of evaluation that is not default.
# This should make tidied code more succinct, which usually results in
# improved legibility.  This fixes a PythonTidy bug noticed by
# Kuang-che Wu having to do with order of evaluation of comparisons.
# 
# o As a matter of style per PEP 308, parentheses are preferred around
# conditional expressions.
# 
# o Give the bitwise invert operator the same precedence as unary plus
# and unary minus.
# 
# I am making other changes to PythonTidy so that a few more of the
# examples from the Python *test* module will pass:
# 
# o Index literal pool by type.  (Use *repr*.)
# 
# o Never append a trailing comma to starred or double-starred
# arguments.
# 
# 2009 Jun 29 . v1.19 . ccr . For Daniel G. Siegel at
# http://home.cs.tum.edu, *python* 2.6 tokenizer returns newlines
# separate from comments, so, though it may be necessary to save
# newlines, it won't do for them to overlay comments.
# 
# 2009 Feb 05 . v1.18 . ccr . For Massimo Di Pierro at
# http://mdp.cti.depaul.edu/, do not break up raw literals.
# 
# 2008 Jan 30 . v1.17 . ccr . This fixes regression in newline support
# introduced at v1.11, which was first reported by Dr0id.
# 
# 2008 Jan 06 . v1.16 . ccr . John Machin demonstrates that hex values
# are not in fact stored in the literal pool.  They should always have
# been and should always be.
# 
# Apparently, doubled number-signs in columns one and two are
# sacrosanct sentinels in Fredrik Lundh's PythonDoc documentation
# generator and must not therefore be disturbed.
# 
# Fix a crash caused by indents' crossing the centerline.
# 
# 2007 May 25 . v1.15 . ccr . Don't split lines in the middle of
# function-parameter assignment.
# 
# Optionally wrap doc strings and comments to COL_LIMIT.
# 
# 2007 May 01, 23, 24 . v1.14 . ccr . Gaëtan de Menten at
# http://openhex.org points out that a null statement is generated by
# a trailing semicolon.  This has been fixed.  He has been helpful by,
# among other things, insisting that I clean up the rendering of doc
# strings and comments.
# 
# Forcing string-literal delimiters to quotes or apostrophes (if
# required) is now done before storing them to the literal pool.
# 
# Wrap chunks of code whose successors cannot be wrapped.
# 
# Don't elide leading tabs in comments and doc strings.  Instead
# substitute DOC_TAB_REPLACEMENT so they can be edited out manually.
# 
# Split long string literals at spaces when CAN_SPLIT_STRINGS is True.
# 
# String literals with attributes are no longer parenthesized.
# 
# For François Pinard, wrap before operators.
# 
# Subscripted class attributes are no longer parenthesized.
# 
# Differentiate MAX_SEPS for different situations.
# 
# 2007 Mar 06 . v1.12 . ccr . The requests of Aaron Bingham: Specify
# boilerplate to be inserted after the module doc string.  Optionally
# split wide string literals at the column limit.  Force trailing
# newline.
# 
# 2007 Jan 22 . v1.11 . ccr . This update implements a couple of
# well-taken user requests:
# 
# Jens Diemer wants a module-level function, *tidy_up*, to accept file
# names or file-like objects.
# 
# Wolfgang Grafen wants trailing spaces eliminated to avoid spurious
# differences with pre-tidied code.
# 
# 2007 Jan 14 . v1.10 . ccr . There was a big problem with earlier
# versions: Canonical values were substituted for strings and numbers.
# For example, decimal integers were substituted for hexadecimal, and
# escaped strings for raw strings.  Authors of Python scripts usually
# use peculiar notations for peculiar purposes, and doing away with
# them negatively impacts the readability of the code.
# 
# This version preserves the original constants (parsed by *tokenize*)
# in a literal pool indexed by the value they evaluate to.  The
# canonical values (output by *compiler*) are then translated back
# (when possible) to the original constants by looking them up in the
# literal pool.
# 
# 2006 Dec 19 . v1.9 . ccr . If class name is a string, pass it to
# personal substitutions routine to distinguish module globals like
# gtk.VBox from class attributes like gtk.Dialog.vbox.
# 
# 2006 Dec 17 . v1.8 . ccr . Trailing comma in function parameter list
# is not allowed in all cases.  Catch substitutions that collide with
# built-ins.
# 
# 2006 Dec 14 . v1.7 . ccr . Track line numbers on output.
# Write a "Name Substitutions Report" on stderr.
# 
# 2006 Dec 13 . v1.6 . ccr . A *yield* may appear in parens when it is
# the subject of an assignment; otherwise, not.
# 
# 2006 Dec 05 . v1.5 . ccr . Strings default to single quotes when
# DOUBLE_QUOTED_STRINGS = False.  Pass the newline convention from
# input to output (transparently :-) ).
# 
# 2006 Dec 01 . v1.4 . ccr . Tighten qualifications for in-line
# comments.  Decode string nodes.  Enclose doc strings in double
# quotes.  Allow file-name arguments.
# 
# 2006 Nov 30 . v1.3 . ccr . Safe check against names of *compiler* .
# abstract syntax tree nodes rather than their classes to step around
# one Python Version Dependency.
#@-<< version history >>
#@+<< data >>
#@+node:ekr.20141010141310.18628: ** << data >>
# Global objects...
# EKR: define these here to avoid a pylint warning.
COMMENTS = None
INPUT = None
INPUT_CODING = None
NAME_SPACE = None
OUTPUT = None

# Unpythonic...
# ZERO = 0
# SPACE = ' '
# NULL = ''
# NA = -1
# APOST = "'"

# Old code is parsed.  New code is generated from the parsed version,
# using these literals:

COL_LIMIT = 72
INDENTATION = '    '
ASSIGNMENT = ' = '
FUNCTION_PARAM_ASSIGNMENT = '='
FUNCTION_PARAM_SEP = ', '
LIST_SEP = ', '
SUBSCRIPT_SEP = ', '
DICT_COLON = ': '
SLICE_COLON = ':'
COMMENT_PREFIX = '# '
SHEBANG = '#!/usr/bin/python'
CODING = 'utf-8'
CODING_SPEC = '# -*- coding: %s -*-' % CODING
BOILERPLATE = ''
BLANK_LINE = ''

LOCAL_NAME_SCRIPT = []
GLOBAL_NAME_SCRIPT = []
CLASS_NAME_SCRIPT = []
FUNCTION_NAME_SCRIPT = []

    # It is not wise to monkey with the
    # spelling of function names (methods)
    # where they are defined unless you are
    # willing to change their spelling where
    # they are referred to as class
    # attributes, too.

FORMAL_PARAM_NAME_SCRIPT = []

    # It is not wise to monkey with the
    # spelling of formal parameters for fear
    # of changing those of functions
    # (methods) defined in other modules.

ATTR_NAME_SCRIPT = []

    # It is not wise to monkey with the
    # spelling of attributes (methods) for
    # fear of changing those of classes
    # defined in other modules.

# Other global constants:
    
# pylint: disable=anomalous-backslash-in-string

UNDERSCORE_PATTERN = re.compile('(?<=[a-z])([A-Z])')
COMMENT_PATTERN = re.compile('([^#]*?)#\s?')
SHEBANG_PATTERN = re.compile('#!')
CODING_PATTERN = re.compile('coding[=:]\\s*([.\\w\\-_]+)')
NEW_LINE_PATTERN = re.compile(r'(?<!\\)(?:(?:\\n)|\n)')
PGRAPH_PATTERN = re.compile(r'\n{2,}')
UNIVERSAL_NEW_LINE_PATTERN = re.compile(r'((?:\r\n)|(?:\r)|(?:\n))')
QUOTE_PATTERN = re.compile('([rRuU]{,2})((?:"{3})|(?:\'{3})|(?:")|(?:\'))')
ELIDE_C_PATTERN = re.compile('^c([A-Z])')
ELIDE_A_PATTERN = re.compile('^a([A-Z])')
ELIDE_F_PATTERN = re.compile('^f([A-Z])')
DOC_WRAPPER = textwrap.TextWrapper(
#    width=COL_LIMIT,  #  2012 May 23
    expand_tabs=True,
    replace_whitespace=True,
    initial_indent='',
    subsequent_indent='',
    fix_sentence_endings=False,
    break_long_words=True,
    )
SUBSTITUTE_FOR = {
    'abday_1':'ABDAY_1',
    'abday_2':'ABDAY_2',
    'abday_3':'ABDAY_3',
    'abday_4':'ABDAY_4',
    'abday_5':'ABDAY_5',
    'abday_6':'ABDAY_6',
    'abday_7':'ABDAY_7',
    'abmon_1':'ABMON_1',
    'abmon_10':'ABMON_10',
    'abmon_11':'ABMON_11',
    'abmon_12':'ABMON_12',
    'abmon_2':'ABMON_2',
    'abmon_3':'ABMON_3',
    'abmon_4':'ABMON_4',
    'abmon_5':'ABMON_5',
    'abmon_6':'ABMON_6',
    'abmon_7':'ABMON_7',
    'abmon_8':'ABMON_8',
    'abmon_9':'ABMON_9',
    'accel_group': 'AccelGroup',
    'action_default': 'ACTION_DEFAULT',
    'action_copy': 'ACTION_COPY',
    'align_left': 'ALIGN_LEFT',
    'align_right': 'ALIGN_RIGHT',
    'align_center': 'ALIGN_CENTER',
    'alignment': 'Alignment',
    'button_press': 'BUTTON_PRESS',
    'button_press_mask': 'BUTTON_PRESS_MASK',
    'buttons_cancel': 'BUTTONS_CANCEL', 
    'can_default': 'CAN_DEFAULT',
    'can_focus': 'CAN_FOCUS',
    'cell_renderer_pixbuf': 'CellRendererPixbuf',
    'cell_renderer_text': 'CellRendererText',
    'check_button': 'CheckButton',
    'child_nodes': 'childNodes',
    'color': 'Color',
    'config_parser': 'ConfigParser',
    'cursor': 'Cursor',
    'day_1':'DAY_1',
    'day_2':'DAY_2',
    'day_3':'DAY_3',
    'day_4':'DAY_4',
    'day_5':'DAY_5',
    'day_6':'DAY_6',
    'day_7':'DAY_7',
    'dest_default_all': 'DEST_DEFAULT_ALL',
    'dialog_modal': 'DIALOG_MODAL', 
    'dict_reader': 'DictReader', 
    'dict_writer': 'DictWriter', 
    'dir_tab_forward': 'DIR_TAB_FORWARD',
    'dotall': 'DOTALL',
    'enter_notify_mask': 'ENTER_NOTIFY_MASK',
    'error': 'Error',
    'event_box': 'EventBox', 
    'expand': 'EXPAND',
    'exposure_mask': 'EXPOSURE_MASK',
    'file_selection': 'FileSelection',
    'fill': 'FILL',
    'ftp': 'FTP',
    'get_attribute': 'getAttribute',
    'gtk.button': 'Button',
    'gtk.combo': 'Combo',
    'gtk.dialog': 'Dialog',
    'gtk.entry': 'Entry',
    'pixmap': 'Pixmap',
    'gtk.image': 'Image',
    'gtk.label': 'Label',
    'gtk.menu': 'Menu',
    'gtk.pack_end': 'PACK_END',
    'gtk.pack_start': 'PACK_START',
    'gtk.vbox': 'VBox',
    'gtk.window': 'Window',
    'hand2': 'HAND2',
    'hbox': 'HBox', 
    'icon_size_button': 'ICON_SIZE_BUTTON', 
    'icon_size_dialog': 'ICON_SIZE_DIALOG',
    'icon_size_dnd': 'ICON_SIZE_DND',
    'icon_size_large_toolbar': 'ICON_SIZE_LARGE_TOOLBAR',
    'icon_size_menu': 'ICON_SIZE_MENU',
    'icon_size_small_toolbar': 'ICON_SIZE_SMALL_TOOLBAR',
    'image_menu_item': 'ImageMenuItem',
    'item_factory': 'ItemFactory',
    'justify_center': 'JUSTIFY_CENTER',
    'justify_fill': 'JUSTIFY_FILL',
    'justify_left': 'JUSTIFY_LEFT',
    'justify_right': 'JUSTIFY_RIGHT',
    'list_item': 'ListItem',
    'list_store': 'ListStore',
    'menu_bar': 'MenuBar',
    'message_dialog': 'MessageDialog', 
    'message_info': 'MESSAGE_INFO', 
    'mon_1':'MON_1',
    'mon_10':'MON_10',
    'mon_11':'MON_11',
    'mon_12':'MON_12',
    'mon_2':'MON_2',
    'mon_3':'MON_3',
    'mon_4':'MON_4',
    'mon_5':'MON_5',
    'mon_6':'MON_6',
    'mon_7':'MON_7',
    'mon_8':'MON_8',
    'mon_9':'MON_9',
    'multiline': 'MULTILINE',
    'node_type': 'nodeType',
    'notebook': 'Notebook',
    'o_creat': 'O_CREAT', 
    'o_excl': 'O_EXCL',
    'o_ndelay': 'O_NDELAY',
    'o_rdwr': 'O_RDWR', 
    'p_nowait':'P_NOWAIT',
    'parsing_error': 'ParsingError',
    'pointer_motion_mask': 'POINTER_MOTION_MASK',
    'pointer_motion_hint_mask': 'POINTER_MOTION_HINT_MASK',
    'policy_automatic': 'POLICY_AUTOMATIC',
    'policy_never': 'POLICY_NEVER',
    'radio_button': 'RadioButton',
    'realized': 'REALIZED',
    'relief_none': 'RELIEF_NONE',
    'request':'Request',
    'response_cancel': 'RESPONSE_CANCEL', 
    'response_delete_event': 'RESPONSE_DELETE_EVENT',
    'response_no': 'RESPONSE_NO',
    'response_none': 'RESPONSE_NONE',
    'response_ok': 'RESPONSE_OK', 
    'response_yes': 'RESPONSE_YES',
    'scrolled_window': 'ScrolledWindow',
    'shadow_in': 'SHADOW_IN',
    'sniffer': 'Sniffer', 
    'sort_ascending': 'SORT_ASCENDING',
    'sort_descending': 'SORT_DESCENDING',
    'state_normal': 'STATE_NORMAL',
    'stock_add': 'STOCK_ADD',
    'stock_apply': 'STOCK_APPLY', 
    'stock_bold': 'STOCK_BOLD',
    'stock_cancel': 'STOCK_CANCEL',
    'stock_close': 'STOCK_CLOSE',
    'stock_convert': 'STOCK_CONVERT',
    'stock_copy': 'STOCK_COPY',
    'stock_cut': 'STOCK_CUT',
    'stock_dialog_info': 'STOCK_DIALOG_INFO',
    'stock_dialog_question': 'STOCK_DIALOG_QUESTION',
    'stock_execute': 'STOCK_EXECUTE', 
    'stock_find': 'STOCK_FIND',
    'stock_find_and_replace': 'STOCK_FIND_AND_REPLACE',
    'stock_go_back': 'STOCK_GO_BACK',
    'stock_go_forward': 'STOCK_GO_FORWARD',
    'stock_help': 'STOCK_HELP',
    'stock_index': 'STOCK_INDEX',
    'stock_jump_to': 'STOCK_JUMP_TO',
    'stock_new': 'STOCK_NEW',
    'stock_no': 'STOCK_NO',
    'stock_ok': 'STOCK_OK',
    'stock_open': 'STOCK_OPEN',
    'stock_paste': 'STOCK_PASTE',
    'stock_preferences': 'STOCK_PREFERENCES',
    'stock_print_preview': 'STOCK_PRINT_PREVIEW',
    'stock_quit': 'STOCK_QUIT',
    'stock_refresh': 'STOCK_REFRESH',
    'stock_remove': 'STOCK_REMOVE',
    'stock_save': 'STOCK_SAVE',
    'stock_save_as': 'STOCK_SAVE_AS',
    'stock_yes': 'STOCK_YES',
    'string_io': 'StringIO',
    'style_italic': 'STYLE_ITALIC',
    'sunday': 'SUNDAY',
    'tab': 'Tab',
    'tab_array': 'TabArray',
    'tab_left': 'TAB_LEFT',
    'table': 'Table',
    'target_same_app': 'TARGET_SAME_APP',
    'target_same_widget': 'TARGET_SAME_WIDGET',
    'text_iter': 'TextIter',
    'text_node': 'TEXT_NODE',
    'text_tag': 'TextTag',
    'text_view': 'TextView',
    'text_window_text': 'TEXT_WINDOW_TEXT',
    'text_window_widget': 'TEXT_WINDOW_WIDGET',
    'text_wrapper':'TextWrapper',
    'tooltips': 'Tooltips', 
    'tree_view': 'TreeView',
    'tree_view_column': 'TreeViewColumn',
    'type_string': 'TYPE_STRING',
    'underline_single': 'UNDERLINE_SINGLE',
    'weight_bold': 'WEIGHT_BOLD',
    'window_toplevel': 'WINDOW_TOPLEVEL', 
    'wrap_none': 'WRAP_NONE',
    'wrap_word': 'WRAP_WORD',
    }
#@-<< data >>
#@+<< preferences >>
#@+node:ekr.20141010141310.19073: ** << preferences >>
KEEP_BLANK_LINES = True
ADD_BLANK_LINES_AROUND_COMMENTS = True
MAX_SEPS_FUNC_DEF = 3
MAX_SEPS_FUNC_REF = 5
MAX_SEPS_SERIES = 5
MAX_SEPS_DICT = 3
MAX_LINES_BEFORE_SPLIT_LIT = 2
LEFT_MARGIN = ''
LEFTJUST_DOC_STRINGS = False
WRAP_DOC_STRINGS = False
DOUBLE_QUOTED_STRINGS = False
SINGLE_QUOTED_STRINGS = False
RECODE_STRINGS = False
OVERRIDE_NEWLINE = None
CAN_SPLIT_STRINGS = False
DOC_TAB_REPLACEMENT = '....'
KEEP_UNASSIGNED_CONSTANTS = False
PARENTHESIZE_TUPLE_DISPLAY = True
JAVA_STYLE_LIST_DEDENT = False

# Author's preferences:

if PERSONAL:
    LEFTJUST_DOC_STRINGS = True
    LOCAL_NAME_SCRIPT.extend([unmangle, camel_case_to_underscore])
    GLOBAL_NAME_SCRIPT.extend([unmangle, camel_case_to_underscore, 
                              all_upper_case])
    CLASS_NAME_SCRIPT.extend([elide_c, underscore_to_camel_case])
    FUNCTION_NAME_SCRIPT.extend([camel_case_to_underscore])
    FORMAL_PARAM_NAME_SCRIPT.extend([elide_a, camel_case_to_underscore])
    ATTR_NAME_SCRIPT.extend([elide_f, camel_case_to_underscore, 
                            substitutions])
#@-<< preferences >>
#@+others
#@+node:ekr.20141010141310.18629: ** Name-transformation functions:

#@+node:ekr.20141010141310.18630: *3* all_lower_case
def all_lower_case(str, **attribs):
    return str.lower()


#@+node:ekr.20141010141310.18631: *3* all_upper_case
def all_upper_case(str, **attribs):
    return str.upper()


#@+node:ekr.20141010141310.18637: *3* camel_case_to_underscore
def camel_case_to_underscore(str, **attribs):
    if is_magic(str):
        return str
    else:
        return all_lower_case(insert_underscores(str))


#@+node:ekr.20141010141310.18642: *3* elide_a
def elide_a(str, **attribs):
    return ELIDE_A_PATTERN.sub('\\1', str)


#@+node:ekr.20141010141310.18641: *3* elide_c
def elide_c(str, **attribs):
    return ELIDE_C_PATTERN.sub('\\1', str)


#@+node:ekr.20141010141310.18643: *3* elide_f
def elide_f(str, **attribs):
    return ELIDE_F_PATTERN.sub('\\1', str)


#@+node:ekr.20141010141310.18634: *3* insert_underscores
def insert_underscores(str, **attribs):
    return UNDERSCORE_PATTERN.sub('_\\1', str)


#@+node:ekr.20141010141310.18635: *3* is_magic
def is_magic(str):
    return str in ['self', 'cls'] or str.startswith('__') and str.endswith('__')


#@+node:ekr.20141010141310.18639: *3* munge
def munge(str, **attribs):
    """Create an unparsable name.

    """

    return '<*%s*>' % str


#@+node:ekr.20141010141310.18633: *3* strip_underscores
def strip_underscores(str, **attribs):
    return str.replace('_', '')


#@+node:ekr.20141010141310.18640: *3* substitutions
def substitutions(str, **attribs):
    result = SUBSTITUTE_FOR.get(str, str)
    module = attribs.get('module')
    if module is None:
        pass
    else:
        result = SUBSTITUTE_FOR.get('%s.%s' % (module, str), result)
    return result


#@+node:ekr.20141010141310.18632: *3* title_case
def title_case(str, **attribs):
    return str.title()


#@+node:ekr.20141010141310.18636: *3* underscore_to_camel_case
def underscore_to_camel_case(str, **attribs):
    if is_magic(str):
        return str
    else:
        return strip_underscores(title_case(camel_case_to_underscore(str)))


#@+node:ekr.20141010141310.18638: *3* unmangle
def unmangle(str, **attribs):
    if str.startswith('__'):
        str = str[2:]
    return str


#@+node:ekr.20141010141310.18644: ** Name-transformation scripts:
#@+node:ekr.20141010141310.18645: *3* force_quote
def force_quote(encoded, double=True, quoted=True):

    r"""Change the type of quotation marks (or not) on an already quoted string.

    >>> force_quote("See the cat.", quoted=False)
    '"See the cat."'
    >>> force_quote("'See the cat.'")
    '"See the cat."'
    >>> force_quote("'See the cat.'", double=False)
    "'See the cat.'"
    >>> force_quote('"See the cat."')
    '"See the cat."'
    >>> force_quote('"See the cat."', double=False)
    "'See the cat.'"
    >>> force_quote('"\"That\'s that,\" said the cat."')
    '"\\"That\'s that,\\" said the cat."'
    >>> force_quote('"\"That\'s that,\" said the cat."', double=False)
    '\'"That\\\'s that," said the cat.\''
    >>> force_quote("'\"That\'s that,\" said the cat.'")
    '"\\"That\'s that,\\" said the cat."'
    >>> force_quote("ru'ick'")
    'ru"ick"'
    >>> force_quote("ru'ick'", double=False)
    "ru'ick'"
    >>> force_quote('ru"ick"')
    'ru"ick"'
    >>> force_quote('ru"ick"', double=False)
    "ru'ick'"
    >>> force_quote("'''ick'''", double=False)
    "'''ick'''"

    """

    if quoted:
        match = QUOTE_PATTERN.match(encoded)
        if match is None:
            prefix = ''
            size = 1
        else:
            (prefix, quote_old) = match.group(1, 2)
            encoded = QUOTE_PATTERN.sub('', encoded, 1)
            size = len(quote_old)
            assert encoded[-size:] == quote_old
            encoded = encoded[:-size]
    else:
        prefix = ''
        size = 1
    double_backslash_delimited_substrings = encoded.split(r'\\')
    for (ndx, substring) in enumerate(double_backslash_delimited_substrings):
        substring = substring.replace(r'\"', '"').replace(r"\'", "'")
        if double:
            substring = substring.replace('"', r'\"')
        else:
            substring = substring.replace("'", r"\'")
        double_backslash_delimited_substrings[ndx] = substring
    encoded = r'\\'.join(double_backslash_delimited_substrings)
    if double:
        quote_new = '"' * size
    else:
        quote_new = "'" * size
    result = ''.join([prefix, quote_new, encoded, quote_new])
    return result
#@+node:ekr.20141010141310.18646: *3* wrap_lines
def wrap_lines(
    lines,
    width,
    initial_indent='',
    subsequent_indent='',
): 

    """Wrap lines of text, preserving blank lines.

    Lines is a Python list of strings *without* new-line terminators.

    Initial_indent is a string that will be prepended to the first
    line of wrapped output.

    Subsequent_indent is a string that will be prepended to all lines
    of wrapped output except the first.

    The result is a Python list of strings *without* new-Line terminators.

    >>> print '\\n'.join(wrap_lines('''Now is the time
    ... for every good man
    ... to come to the aid of his party.
    ... 
    ... 
    ... Don't pass the buck
    ... but give your buck
    ... to the party of your choice.'''.splitlines(), width=40))
    Now is the time for every good man to
    come to the aid of his party.
    <BLANKLINE>
    Don't pass the buck but give your buck
    to the party of your choice.

    """

    DOC_WRAPPER.width = width
    DOC_WRAPPER.initial_indent = initial_indent
    DOC_WRAPPER.subsequent_indent = subsequent_indent
    result = [line.strip() for line in lines]
    result = '\n'.join(result)
    pgraphs = PGRAPH_PATTERN.split(result)
    result = []
    while pgraphs:
        pgraph = DOC_WRAPPER.fill(pgraphs.pop(0))
        result.extend(pgraph.splitlines())
        if pgraphs:
            result.append('')
    return result
#@+node:ekr.20141010141310.18647: *3* leftjust_lines
def leftjust_lines(lines):

    """Left justify lines of text.

    Lines is a Python list of strings *without* new-line terminators.

    The result is a Python list of strings *without* new-Line terminators.

    """

    result = [line.strip() for line in lines]
    return result
#@+node:ekr.20141010141310.19063: ** classes
#@+node:ekr.20141010141310.18648: *3* class InputUnit
class InputUnit(object):

    """File-buffered wrapper for sys.stdin.

    """
    #@+others
    #@+node:ekr.20141010141310.18649: *4* __init__

    def __init__(self, file_in):
        object.__init__(self)
        self.is_file_like = hasattr(file_in, 'read')
        if self.is_file_like:
            buffer = file_in.read()
        else:
            unit = open(os.path.expanduser(file_in), 'rb')
            buffer = unit.read()
            unit.close()
        self.lines = UNIVERSAL_NEW_LINE_PATTERN.split(buffer)
        if len(self.lines) > 2:
            if OVERRIDE_NEWLINE is None:
                self.newline = self.lines[1]  # ... the first delimiter.
            else:
                self.newline = OVERRIDE_NEWLINE
            look_ahead = '\n'.join([self.lines[0], self.lines[2]])
        else:
            self.newline = '\n'
            look_ahead = ''
        match = CODING_PATTERN.search(look_ahead)
        if match is None:
            self.coding = 'ascii'
        else:
            self.coding = match.group(1)
        self.rewind()
        return

    #@+node:ekr.20141010141310.18650: *4* rewind
    def rewind(self):
        self.ndx = 0
        self.end = len(self.lines) - 1
        return self

    #@+node:ekr.20141010141310.18651: *4* next
    def next(self):
        if self.ndx > self.end:
            raise StopIteration
        elif self.ndx == self.end:
            result = self.lines[self.ndx]
        else:
            result = self.lines[self.ndx] + '\n'
        self.ndx += 2
        return result

    #@+node:ekr.20141010141310.18652: *4* __iter__
    def __iter__(self):
        return self

    #@+node:ekr.20141010141310.18653: *4* readline
    def readline(self):
        try:
            result = self.next()
        except StopIteration:
            result = ''
        return result

    #@+node:ekr.20141010141310.18654: *4* readlines
    def readlines(self):
        self.rewind()
        return [line for line in self]

    #@+node:ekr.20141010141310.18655: *4* __str__
    def __str__(self):
        result = self.readlines()
        while result[:-1] == '':
            result.pop(-1)
        last_line = result[-1]
        if last_line[:-1] == '\n':
            pass
        else:
            last_line += '\n'
            result[-1] = last_line
        return ''.join(result)

    #@+node:ekr.20141010141310.18656: *4* decode
    def decode(self, str):
        return str  # It will not do to feed Unicode to *compiler.parse*.


    #@-others
#@+node:ekr.20141010141310.18657: *3* class OutputUnit
class OutputUnit(object):

    """Line-buffered wrapper for sys.stdout.

    """
    #@+others
    #@+node:ekr.20141010141310.18658: *4* __init__

    def __init__(self, file_out):
        object.__init__(self)
        self.is_file_like = hasattr(file_out, 'write')
        if self.is_file_like:
            self.unit = codecs.getwriter(CODING)(file_out)
        else:
            self.unit = codecs.open(os.path.expanduser(file_out), 'wb', CODING)
        self.blank_line_count = 1
        self.margin = LEFT_MARGIN
        self.newline = INPUT.newline
        self.lineno = 0
        self.buffer = ''
        self.chunks = None
        return

    #@+node:ekr.20141010141310.18659: *4* close
    def close(self):
        self.unit.write(self.buffer)
        if self.is_file_like:
            pass
        else:
            self.unit.close()
        return self

    #@+node:ekr.20141010141310.18660: *4* line_init
    def line_init(self, indent=0, lineno=0):
        self.blank_line_count = 0
        self.col = 0
        if DEBUG:
            margin = '%5i %s' % (lineno, INDENTATION * indent)
        else:
            margin = self.margin + INDENTATION * indent
        self.tab_stack = []
        self.tab_set(len(margin) + len(INDENTATION))
        self.chunks = []
        self.line_more(margin)
        return self

    #@+node:ekr.20141010141310.18661: *4* line_more
    def line_more(
        self,
        chunk='',
        tab_set=False,
        tab_clear=False, 
        can_split_str=False,
        can_split_after=False,
        can_break_after=False,
        ):
        self.chunks.append([
            chunk,
            tab_set,
            tab_clear,
            can_split_str,
            can_split_after, 
            can_break_after,
            ])
        self.col += len(chunk)
        return self

    #@+node:ekr.20141010141310.18662: *4* line_term
    def line_term(self, pause=False):

        def is_split_needed(cumulative_width):
            pos = self.pos
            return ((pos + cumulative_width) > COL_LIMIT) and (pos > 0)

        def drop_word(chunk, can_split_after):
            result = COL_LIMIT - self.pos
            if can_split_after:
                result -= 1
            else:
                result -= 2
            ndx = result - 1
            while (ndx >= 20) and ((result - ndx) <= 20):
                if chunk[ndx] in [' ']:
                    result = ndx + 1
                    break
                ndx -= 1
            return result

        self.pos = 0
        can_split_before = False
        can_break_before = False
        cumulative_width = 0
        chunk_lengths = []
        self.chunks.reverse()
        for (
            chunk,
            tab_set,
            tab_clear,
            can_split_str,
            can_split_after,
            can_break_after,
            ) in self.chunks:
            if can_split_after or can_break_after:
                cumulative_width = 0
            cumulative_width += len(chunk)
            chunk_lengths.insert(0, [
                chunk,
                cumulative_width,
                tab_set,
                tab_clear,
                can_split_str,
                can_split_after,
                can_break_after,
                ])
        for (
            chunk,
            cumulative_width,
            tab_set,
            tab_clear,
            can_split_str,
            can_split_after,
            can_break_after,
            ) in chunk_lengths:
            if is_split_needed(cumulative_width):
                if can_split_before:
                    self.line_split()
                elif can_break_before:
                    self.line_break()
            if can_split_str:
                quote = chunk[:1]
                while is_split_needed(len(chunk)):
                    take = drop_word(chunk, can_split_after)
                    if take < 20:
                        break
                    self.put(chunk[:take] + quote)
                    chunk = quote + chunk[take:]
                    if can_split_after:
                        self.line_split()
                    else:
                        self.line_break()
                self.put(chunk)
            else:
                self.put(chunk)
            self.pos += len(chunk)
            if tab_set:
                self.tab_set(self.pos)
            if tab_clear:
                self.tab_clear()
            can_split_before = can_split_after
            can_break_before = can_break_after
        if pause:
            pass
        else:
            self.put(self.newline)
        return self

    #@+node:ekr.20141010141310.18663: *4* line_split
    def line_split(self):
        self.put(self.newline)
        self.pos = self.tab_forward()
        return self

    #@+node:ekr.20141010141310.18664: *4* line_break
    def line_break(self):
        self.put('\\%s' % self.newline)
        self.pos = self.tab_forward()
        return self

    #@+node:ekr.20141010141310.18665: *4* tab_forward
    def tab_forward(self):
        if len(self.tab_stack) > 1:
            col = (self.tab_stack)[1]
        else:
            col = (self.tab_stack)[0]
        self.put(' ' * col)
        return col

    #@+node:ekr.20141010141310.18666: *4* put
    def put(self, text):
        self.lineno += text.count(self.newline)
        self.buffer += text
        if self.buffer.endswith('\n') or self.buffer.endswith('\r'):
            self.unit.write(self.buffer.rstrip())
            self.unit.write(self.newline)
            self.buffer = ''
        return self

    #@+node:ekr.20141010141310.18667: *4* put_blank_line
    def put_blank_line(self, trace, count=1):
        count -= self.blank_line_count
        while count > 0:
            self.put(BLANK_LINE)
            self.put(self.newline)
            if DEBUG:
                self.put('blank(%s)' % str(trace))
            self.blank_line_count += 1
            count -= 1
        return self

    #@+node:ekr.20141010141310.18668: *4* tab_set
    def tab_set(self, col):
        if col > COL_LIMIT / 2:
            if self.tab_stack:
                col = (self.tab_stack)[-1] + 4
            else:
                col = 4
        self.tab_stack.append(col)
        return self

    #@+node:ekr.20141010141310.18669: *4* tab_clear
    def tab_clear(self):
        if len(self.tab_stack) > 1:
            result = self.tab_stack.pop()
        else:
            result = None
        return result

    #@+node:ekr.20141010141310.18670: *4* inc_margin
    def inc_margin(self):
        self.margin += INDENTATION
        return self

    #@+node:ekr.20141010141310.18671: *4* dec_margin
    def dec_margin(self):
        self.margin = (self.margin)[:-len(INDENTATION)]
        return self


    #@-others
#@+node:ekr.20141010141310.18672: *3* class Comments
class Comments(dict):

    """Collection of comments (blank lines) parsed out of the
    input Python code and indexed by line number.

    """
    #@+others
    #@+node:ekr.20141010141310.18673: *4* __init__
    def __init__(self,is_module):

        def quote_original(token_type, original):
            if token_type in [tokenize.STRING]:
                if DOUBLE_QUOTED_STRINGS:
                    result = force_quote(original, double=True)
                elif SINGLE_QUOTED_STRINGS:
                    result = force_quote(original, double=False)
                else:
                    result = original
            else:
                result = original
            return result

        def compensate_for_tabs(line, scol):
            match = COMMENT_PATTERN.match(line)
            if match is None:
                pass
            else:
                margin = match.group(1)
                tab_count = margin.count('\t')
                scol += (len(INDENTATION) - 1) * tab_count
            return scol

        def merge_concatenated_strings(lines):

            """Save whole string in literal pool.

            Python (and the *compiler* module) treat adjacent strings
            without an intervening operator as one string.  The
            *tokenize* module does not.  Thus, although the parts are
            easily saved in PythonTidy's literal pool, the whole
            string is not.  This routine makes a full pass through the
            tokens and accumulates adjacent strings so that the whole
            string is saved in the literal pool along with its
            original spelling.

            This preserves the original spelling of words even in
            especially long phrases that would otherwise be normalized
            with escape sequences for embedded \"special\" characters.

            The original spelling is stored in the literal pool,
            indexed by the normalized version.  If a lookup of the
            normalized version succeeds, the original spelling is
            output; otherwise, the normalized version is used instead.

            """
            try:
                while True:
                    prev_item = lines.next()
                    yield prev_item
                    (   prev_token_type,
                        prev_token_string,
                        prev_start,
                        prev_end,
                        prev_line,
                        ) = prev_item
                    if prev_token_type in [tokenize.STRING]:
                        on1 = True
                        while True:
                            next_item  = lines.next()
                            yield next_item
                            (   next_token_type,
                                next_token_string,
                                next_start,
                                next_end,
                                next_line,
                            ) = next_item
                            if next_token_type in [tokenize.STRING]:
                                if prev_token_string[-1] == next_token_string[0]:
                                    prev_token_string = prev_token_string[:-1] + \
                                                        next_token_string[1:]
                                    on1 = False
                            else:
                                if on1:
                                    pass
                                else:
                                    prev_item = (
                                        prev_token_type,
                                        prev_token_string,
                                        prev_start,
                                        prev_end,
                                        prev_line,
                                        )
                                    yield prev_item
                                    break
            except NotImplementedError:
                pass
            return

        self.literal_pool = {}
        lines = tokenize.generate_tokens(INPUT.readline)
        lines = merge_concatenated_strings(lines)
        for (token_type, token_string, start, end, line) in lines:
            if DEBUG:
                print (token.tok_name)[token_type], token_string, start, \
                    end, line
            (self.max_lineno, scol) = start
            (erow, ecol) = end
            if token_type in [tokenize.COMMENT, tokenize.NL]:
                original = token_string
                original = original.decode(INPUT.coding)
                original = original.replace('\t', DOC_TAB_REPLACEMENT)
                original = original.strip()
                if SHEBANG_PATTERN.match(original) is not None:
                    pass
                elif CODING_PATTERN.search(original) is not None and \
                    self.max_lineno <= 2:
                    pass
                else:
                    scol = compensate_for_tabs(line, scol)
                    original = COMMENT_PATTERN.sub('', original, 1)
                    if (token_type in [tokenize.COMMENT]) and (original in ['']):
                        original = ' '
                    if self.max_lineno in self:
                        pass
                    else:
                        self[self.max_lineno] = [scol, original]
            elif token_type in [tokenize.NUMBER, tokenize.STRING]:
                try:
                    original = token_string.strip().decode(INPUT.coding, 'backslashreplace')
                    decoded = eval(original)
                    encoded = repr(decoded)
                    if (encoded == original) or (encoded == force_quote(original, double=False)):
                        pass
                    else:
                        original = quote_original(token_type, original)
                        original_values = \
                            self.literal_pool.setdefault(encoded, [])
                        for (tok, lineno) in original_values:
                            if tok == original:
                                break
                        else:
                            original_values.append([original, self.max_lineno])
                except:
                    pass
        self.prev_lineno = -2
        if is_module:
            self[self.prev_lineno] = (-1, SHEBANG)
            self[-1] = (-1, CODING_SPEC)
    #@+node:ekr.20141010141310.18674: *4* merge
    def merge(self, lineno=None, fin=False):

        def is_blank():
            return token_string in ['', BLANK_LINE]

        def is_blank_line_needed():
            return ADD_BLANK_LINES_AROUND_COMMENTS and not (is_blank() and
                    KEEP_BLANK_LINES)

        def margin(scol):
            (quotient, remainder) = divmod(scol, len(INDENTATION))
            result = INDENTATION * quotient + ' ' * remainder + COMMENT_PREFIX
            return result

        def strip_blank_lines(text_lines):
            first = -1
            last = -1
            is_first_blank = False
            is_last_blank = False
            if text_lines:
                first = 0
                (scol, line) = text_lines[first]
                is_first_blank = (scol == -1)
                if is_first_blank:
                    first += 1
                last = len(text_lines)
                (scol, line) = text_lines[last - 1]
                is_last_blank = (scol == -1)
                if is_last_blank:
                    last -= 1
            return (first, last, is_first_blank, is_last_blank)

        if fin:
            lineno = self.max_lineno + 1
        on1 = True
        text = []
        while self.prev_lineno < lineno:
            if self.prev_lineno in self:
                (scol, token_string) = self[self.prev_lineno]
                if on1 and is_blank_line_needed():
                    OUTPUT.put_blank_line(1)
                if is_blank():
                    if KEEP_BLANK_LINES:
                        # OUTPUT.put_blank_line(2)
                        text.append([-1, ''])
                else:
                    if scol == -1:

                        # Output the Shebang and Coding-Spec.

                        OUTPUT.line_init().line_more(token_string).line_term()
                    else:
                        text.append([scol, token_string])
                on1 = False
            self.prev_lineno += 1
        if text and LEFTJUST_DOC_STRINGS:
            (first, last, is_first_blank, is_last_blank) = strip_blank_lines(text)
            lines = [line for (scol, line) in text[first: last]]
            lines = leftjust_lines(lines)
            text = [(0, line) for line in lines]
            if is_first_blank:
                text.insert(0, [-1, ''])
            if is_last_blank:
                text.append([-1, ''])
        if text and WRAP_DOC_STRINGS:
            (first, last, is_first_blank, is_last_blank) = strip_blank_lines(text)
            text = text[first: last]
            if text:
                (save_col, line) = text[0]
                lines = [line for (scol, line) in text]
                line_length = COL_LIMIT - (save_col + len(COMMENT_PREFIX))
                line_length = max(line_length, 20)
                lines = wrap_lines(lines, width=line_length)
                text = [(save_col, line) for line in lines]
                if is_first_blank:
                    text.insert(0, [-1, ''])
                if is_last_blank:
                    text.append([-1, ''])
        for (scol, line) in text:
            if scol == -1:
                OUTPUT.put_blank_line(2)
            else:
                OUTPUT.line_init()
                margin_string = margin(scol)
                if (margin_string == '# ') and (line.startswith('#')):
                    OUTPUT.line_more('#')
                else:
                    OUTPUT.line_more(margin(scol))
                OUTPUT.line_more(line)
                OUTPUT.line_term()
        if text and is_blank_line_needed() and not fin:
            OUTPUT.put_blank_line(3)
        return self

    #@+node:ekr.20141010141310.18675: *4* put_inline
    def put_inline(self, lineno):

        def margin(scol):
            result = ' ' * scol + COMMENT_PREFIX
            return result

        def new_line():
            OUTPUT.put(OUTPUT.newline)
            return

        text = []
        while self.prev_lineno <= lineno:
            if self.prev_lineno in self:
                (scol, token_string) = self[self.prev_lineno]
                if token_string in ['']:
                    pass
                else:
                    text.append(token_string)
            self.prev_lineno += 1
        OUTPUT.line_term(pause=True)
        col = OUTPUT.pos + 2
        if WRAP_DOC_STRINGS:
            line_length = COL_LIMIT - (col + len(COMMENT_PREFIX))
            line_length = max(line_length, 20)
            text = wrap_lines(text, width=line_length)
        for line in text[:1]:
            OUTPUT.put(' ' * 2)
            OUTPUT.put(COMMENT_PREFIX)
            OUTPUT.put(line)
            new_line()
        for line in text[1:]:
            OUTPUT.line_init()
            OUTPUT.line_more(margin(col))
            OUTPUT.line_more(line)
            OUTPUT.line_term()
        if text:
            pass
        else:
            new_line()
        return self


    #@-others
#@+node:ekr.20141010141310.19065: *3* Node classes
#@+node:ekr.20141010141310.18676: *4* class Name
class Name(list):

    """Maps new name to old names.

    """
    #@+others
    #@+node:ekr.20141010141310.18677: *5* __init__

    def __init__(self, new):
        self.new = new
        self.is_reported = False
        return

    #@+node:ekr.20141010141310.18678: *5* append
    def append(self, item):
        if item in self:
            pass
        else:
            list.append(self, item)
        return

    #@+node:ekr.20141010141310.18679: *5* rept_collision
    def rept_collision(self, key):
        self.append(key)
        if len(self) == 1:
            pass
        elif self.is_reported:
            pass
        else:
            sys.stderr.write("Error:  %s ambiguously replaced by '%s' at line %i.\n" % \
                             (str(self), self.new, OUTPUT.lineno + 1))
            self.is_reported = True
        return self

    #@+node:ekr.20141010141310.18680: *5* rept_external
    def rept_external(self, expr):
        if isinstance(expr, NodeName):
            expr = expr.name.str
        else:
            expr = str(expr)
        if expr in ['self','cls']:
            pass
        elif self.new == self[0]:
            pass
        else:
            sys.stderr.write("Warning:  '%s.%s,' defined elsewhere, replaced by '.%s' at line %i.\n" % \
                             (expr, self[0], self.new, OUTPUT.lineno + 1))
        return self


    #@-others
#@+node:ekr.20141010141310.18681: *4* class NameSpace
class NameSpace(list):

    """Dictionary of names (variables).

    Actually a list of dictionaries.  The current scope is the top one
    (ZEROth member).

    """
    #@+others
    #@+node:ekr.20141010141310.18682: *5* push_scope
    def push_scope(self):
        self.insert(0, {})
        return self

    #@+node:ekr.20141010141310.18683: *5* pop_scope
    def pop_scope(self):
        return self.pop(0)

    #@+node:ekr.20141010141310.18684: *5* make_name
    def make_name(self, name, rules):
        name = name.get_as_str()
        key = name
        for rule in rules:
            name = rule(name)
        name = self[0].setdefault(name, Name(name))
        self[0].setdefault(key, name)
        name.append(key)
        return name

    #@+node:ekr.20141010141310.18685: *5* make_local_name
    def make_local_name(self, name):
        if self.is_global():
            result = self.make_global_name(name)
        else:
            result = self.make_name(name, LOCAL_NAME_SCRIPT)
        return result

    #@+node:ekr.20141010141310.18686: *5* make_global_name
    def make_global_name(self, name):
        return self.make_name(name, GLOBAL_NAME_SCRIPT)

    #@+node:ekr.20141010141310.18687: *5* make_class_name
    def make_class_name(self, name):
        return self.make_name(name, CLASS_NAME_SCRIPT)

    #@+node:ekr.20141010141310.18688: *5* make_function_name
    def make_function_name(self, name):
        return self.make_name(name, FUNCTION_NAME_SCRIPT)

    #@+node:ekr.20141010141310.18689: *5* make_formal_param_name
    def make_formal_param_name(self, name):
        return self.make_name(name, FORMAL_PARAM_NAME_SCRIPT)

    #@+node:ekr.20141010141310.18690: *5* make_imported_name
    def make_imported_name(self, name):
        return self.make_name(name, [])

    #@+node:ekr.20141010141310.18691: *5* make_attr_name
    def make_attr_name(self, expr, name):
        if isinstance(expr, NodeName):
            module = expr.name.str
        else:
            module = None
        name = name.get_as_str()
        key = name
        for rule in ATTR_NAME_SCRIPT:
            name = rule(name, module=module)
        name = Name(name)
        name.append(key)
        name.rept_external(expr)
        return name.new

    #@+node:ekr.20141010141310.18692: *5* make_keyword_name
    def make_keyword_name(self, name):
        name = name.get_as_str()
        key = name
        for rule in FORMAL_PARAM_NAME_SCRIPT:
            name = rule(name)
        name = Name(name)
        name.append(key)
        return name.new

    #@+node:ekr.20141010141310.18693: *5* get_name
    def get_name(self, node):
        name = key = node.get_as_str()
        for scope in self:
            if key in scope:
                name = scope[key]
                name.rept_collision(key)
                name = name.new
                break
        return name

    #@+node:ekr.20141010141310.18694: *5* has_name
    def has_name(self, node):
        name = node.get_as_str()
        return name in self[0]

    #@+node:ekr.20141010141310.18695: *5* is_global
    def is_global(self):
        return len(self) == 1


    #@-others
#@+node:ekr.20141010141310.18697: *4* class Node
class Node(object):

    """Parent of parsed tokens.

    """

    tag = 'Generic node'

    #@+others
    #@+node:ekr.20141010141310.18698: *5* __init__
    def __init__(self, indent, lineno):
        object.__init__(self)
        self.indent = indent
        self.lineno = lineno
        if DEBUG:
            sys.stderr.write('%5i %s\n' % (self.lineno, self.tag))
        return 

    #@+node:ekr.20141010141310.18699: *5* line_init
    def line_init(self, need_blank_line=0):
        if COMMENTS.prev_lineno > 0:
            OUTPUT.put_blank_line(41, count=need_blank_line)
            need_blank_line -= 1
        COMMENTS.merge(self.get_lineno())
        OUTPUT.put_blank_line(4, count=need_blank_line)
        OUTPUT.line_init(self.indent, self.get_lineno())
        return self

    #@+node:ekr.20141010141310.18700: *5* line_more
    def line_more(
        self,
        chunk='',
        tab_set=False,
        tab_clear=False,
        can_split_str=False,
        can_split_after=False,
        can_break_after=False,
        ):
        OUTPUT.line_more(
            chunk,
            tab_set,
            tab_clear,
            can_split_str,
            can_split_after, 
            can_break_after,
            )
        return self

    #@+node:ekr.20141010141310.18701: *5* line_term
    def line_term(self, lineno=0):
        lineno = max(self.get_hi_lineno(), self.get_lineno())  # , lineno)
        COMMENTS.put_inline(lineno)
        return self

    #@+node:ekr.20141010141310.18702: *5* put
    def put(self, can_split=False):
        '''Place self on output.

        For the "Generic" node, this is abstract.  A Generic node *is*
        instantiated for nodes of unrecognized type, and we don\'t
        know what to do for them, so we just place a string on output
        that should force an error when Python is used to interpret
        the result.

        '''

        self.line_more(' /* %s at line %i */ ' % (self.tag, self.get_lineno()))
        return self

    #@+node:ekr.20141010141310.18703: *5* get_lineno
    def get_lineno(self):
        return self.lineno

    #@+node:ekr.20141010141310.18704: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.get_lineno()

    #@+node:ekr.20141010141310.18705: *5* inc_margin
    def inc_margin(self):
        OUTPUT.inc_margin()
        return self

    #@+node:ekr.20141010141310.18706: *5* dec_margin
    def dec_margin(self):
        OUTPUT.dec_margin()
        return self

    #@+node:ekr.20141010141310.18707: *5* marshal_names
    def marshal_names(self):
        return self

    #@+node:ekr.20141010141310.18708: *5* make_local_name
    def make_local_name(self):
        return self


    #@-others
#@+node:ekr.20141010141310.18709: *4* class NodeOpr
class NodeOpr(Node):

    tag = 'Opr'

    #@+others
    #@+node:ekr.20141010141310.18710: *5* put_expr
    def put_expr(self, node, can_split=False, pos=None):
        if self.is_paren_needed(node, pos):
            self.line_more('(', tab_set=True)
            node.put(can_split=True)
            self.line_more(')', tab_clear=True)
        else:
            node.put(can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18711: *5* is_paren_needed
    def is_paren_needed(self, node, pos):
        return type(node) in OPERATOR_TRUMPS[type(self)]


    #@-others
#@+node:ekr.20141010141310.18712: *4* class NodeOprAssoc
class NodeOprAssoc(NodeOpr):

    tag = 'A_Opr'


#@+node:ekr.20141010141310.18713: *4* class NodeOprNotAssoc
class NodeOprNotAssoc(NodeOpr):

    tag = 'NA_Opr'

    #@+others
    #@+node:ekr.20141010141310.18714: *5* is_paren_needed
    def is_paren_needed(self, node, pos):
        if NodeOpr.is_paren_needed(self, node, pos):
            result = True
        elif type(node) in OPERATOR_LEVEL[type(self)]:
            result = True
        else:
            result = False
        return result


    #@-others
#@+node:ekr.20141010141310.18715: *4* class NodeOprLeftAssoc
class NodeOprLeftAssoc(NodeOpr):

    """Left-associative operator.

    """

    tag = 'LA_Opr'

    #@+others
    #@+node:ekr.20141010141310.18716: *5* is_paren_needed
    def is_paren_needed(self, node, pos):
        if NodeOpr.is_paren_needed(self, node, pos):
            result = True
        elif type(node) in OPERATOR_LEVEL[type(self)]:
            result = not (pos == 'left')
        else:
            result = False
        return result


    #@-others
#@+node:ekr.20141010141310.18717: *4* class NodeOprRightAssoc
class NodeOprRightAssoc(NodeOpr):

    """Right-associative operator.

    """

    tag = 'RA_Opr'

    #@+others
    #@+node:ekr.20141010141310.18718: *5* is_paren_needed
    def is_paren_needed(self, node, pos):
        if NodeOpr.is_paren_needed(self, node, pos):
            if type(node) in [NodeUnaryAdd, NodeUnarySub]:
                result = not (pos == 'right')
            else:
                result = True
        elif type(node) in OPERATOR_LEVEL[type(self)]:
            result = not (pos == 'right')
        else:
            result = False
        return result


    #@-others
#@+node:ekr.20141010141310.18719: *4* class NodeStr
class NodeStr(Node):

    """String value.

    """

    tag = 'Str'

    #@+others
    #@+node:ekr.20141010141310.18720: *5* __init__
    def __init__(self, indent, lineno, str):
        Node.__init__(self, indent, lineno)
        self.set_as_str(str)
        return

    #@+node:ekr.20141010141310.18721: *5* put
    def put(self, can_split=False):
        self.line_more(self.get_as_str())
        return self

    #@+node:ekr.20141010141310.18722: *5* get_as_str
    def get_as_str(self):
        return self.str

    #@+node:ekr.20141010141310.18723: *5* set_as_str
    def set_as_str(self, str_):
        if is_leo:
            self.str = g.toEncodedString(str_)
        else:
            self.str = str_
            if isinstance(self.str, unicode):
                pass
            elif not RECODE_STRINGS:
                pass
            else:
                try:
                    self.str = self.str.decode(INPUT.coding)
                except UnicodeError:
                    pass
                try:
                    self.str = str(self.str)
                except UnicodeError:
                    pass
        return self
    #@+node:ekr.20141010141310.18724: *5* get_as_repr
    def get_as_repr(self):
        original_values = COMMENTS.literal_pool.get(repr(self.get_as_str()), [])
        if len(original_values) == 1:
            (result, lineno) = original_values[0]
        else:
            result = repr(self.get_as_str())
            if DOUBLE_QUOTED_STRINGS:
                result = force_quote(result, double=True)
            elif SINGLE_QUOTED_STRINGS:
                result = force_quote(result, double=False)
        return result

    #@+node:ekr.20141010141310.18725: *5* put_doc
    def put_doc(self, need_blank_line=0):

        def fix_newlines(text):
            lines = text.splitlines()
            result = OUTPUT.newline.join(lines)
            return result

        doc = self.get_as_repr()
        doc = doc.replace('\t', DOC_TAB_REPLACEMENT)
        if LEFTJUST_DOC_STRINGS:
            lines = leftjust_lines(doc.strip().splitlines())
            lines.extend(['', ''])
            margin = '%s%s' % (OUTPUT.newline, INDENTATION * self.indent)
            doc = margin.join(lines)
        if WRAP_DOC_STRINGS:
            margin = '%s%s' % (OUTPUT.newline, INDENTATION * self.indent)
            line_length = COL_LIMIT - (len(INDENTATION) * self.indent)
            line_length = max(line_length, 20)
            lines = wrap_lines(doc.strip().splitlines(), width=line_length)
            lines.extend(['', ''])
            doc = margin.join(lines)
        self.line_init(need_blank_line=need_blank_line)
        doc = fix_newlines(doc)
        self.put_multi_line(doc)
        self.line_term()
        OUTPUT.put_blank_line(5)
        return self

    #@+node:ekr.20141010141310.18726: *5* put_lit
    def put_lit(self, can_split=False):
        lit = self.get_as_repr()
        match = QUOTE_PATTERN.match(lit)
        (prefix, quote) = match.group(1, 2)
        if ('r' in prefix.lower()):
            self.line_more(lit, can_split_str=CAN_SPLIT_STRINGS, can_split_after=can_split)
        else:
            lines = NEW_LINE_PATTERN.split(lit)
            if len(lines) > MAX_LINES_BEFORE_SPLIT_LIT:
                lit = OUTPUT.newline.join(lines)
                self.put_multi_line(lit)
            else:
                self.line_more(lit, can_split_str=CAN_SPLIT_STRINGS, can_split_after=can_split)
        return self

    #@+node:ekr.20141010141310.18727: *5* put_multi_line
    def put_multi_line(self, lit):
        match = QUOTE_PATTERN.match(lit)
        (prefix, quote) = match.group(1, 2)
        if len(quote) == 3:
            head = prefix + quote
            tail = ''
        else:
            head = prefix + quote * 3
            tail = quote * 2
        lit = QUOTE_PATTERN.sub(head, lit, 1) + tail
        self.line_more(lit, can_split_str=False)
        return self


    #@-others
#@+node:ekr.20141010141310.18728: *4* class NodeInt
class NodeInt(Node):

    """Integer value.

    """

    tag = 'Int'

    #@+others
    #@+node:ekr.20141010141310.18729: *5* __init__
    def __init__(self, indent, lineno, int):
        Node.__init__(self, indent, lineno)
        self.int = int
        return 

    #@+node:ekr.20141010141310.18730: *5* put
    def put(self, can_split=False):
        self.line_more(self.get_as_repr())
        return self

    #@+node:ekr.20141010141310.18731: *5* get_as_repr
    def get_as_repr(self):
        original_values = COMMENTS.literal_pool.get(repr(self.int), [])
        if len(original_values) == 1:
            (result, lineno) = original_values[0]
        else:
            result = repr(self.int)
        return result


    #@-others
#@+node:ekr.20141010141310.18732: *4* class NodeAdd
class NodeAdd(NodeOprAssoc):

    """Add operation.

    """

    tag = 'Add'

    #@+others
    #@+node:ekr.20141010141310.18733: *5* __init__
    def __init__(self, indent, lineno, left, right):
        Node.__init__(self, indent, lineno)
        self.left = transform(indent, lineno, left)
        self.right = transform(indent, lineno, right)
        return 

    #@+node:ekr.20141010141310.18734: *5* put
    def put(self, can_split=False):
        self.put_expr(self.left, can_split=can_split)
        self.line_more(' ', can_split_after=can_split, can_break_after=True)
        self.line_more('+ ')
        self.put_expr(self.right, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18735: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.right.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18736: *4* class NodeAnd
class NodeAnd(NodeOprAssoc):

    '''Logical "and" operation.

    '''

    tag = 'And'

    #@+others
    #@+node:ekr.20141010141310.18737: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return 

    #@+node:ekr.20141010141310.18738: *5* put
    def put(self, can_split=False):
        for node in (self.nodes)[:1]:
            self.put_expr(node, can_split=can_split)
        for node in (self.nodes)[1:]:
            self.line_more(' ', can_split_after=can_split, can_break_after=True)
            self.line_more('and ')
            self.put_expr(node, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18739: *5* get_hi_lineno
    def get_hi_lineno(self):
        return (self.nodes)[-1].get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18740: *4* class NodeAsgAttr
class NodeAsgAttr(NodeOpr):

    """Assignment to a class attribute.

    """

    tag = 'AsgAttr'

    #@+others
    #@+node:ekr.20141010141310.18741: *5* __init__
    def __init__(self, indent, lineno, expr, attrname, flags):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        self.attrname = transform(indent, lineno, attrname)
        self.flags = transform(indent, lineno, flags)
        return 

    #@+node:ekr.20141010141310.18742: *5* put
    def put(self, can_split=False):
        is_del = self.flags.get_as_str() in ['OP_DELETE']
        if is_del:
            self.line_init()
            self.line_more('del ')
        if isinstance(self.expr, NodeConst):
            if self.expr.is_str():
                self.expr.put()
            else:
                self.line_more('(')
                self.expr.put(can_split=True)
                self.line_more(')')
        else:
            self.put_expr(self.expr, can_split=can_split)
        self.line_more('.')
        self.line_more(NAME_SPACE.make_attr_name(self.expr, self.attrname))
        if DEBUG:
            self.line_more(' /* AsgAttr flags:  ')
            self.flags.put()
            self.line_more(' */ ')
        if is_del:
            self.line_term()
        return self

    #@+node:ekr.20141010141310.18743: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18744: *4* class NodeAsgList
class NodeAsgList(Node):

    """A list as a destination of an assignment operation.

    """

    tag = 'AsgList'

    #@+others
    #@+node:ekr.20141010141310.18745: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return

    #@+node:ekr.20141010141310.18746: *5* put
    def put(self, can_split=False):
        self.line_more('[', tab_set=True)
        if len(self.nodes) > MAX_SEPS_SERIES:
            self.line_term()
            self.inc_margin()
            for node in self.nodes:
                self.line_init()
                node.put(can_split=True)
                self.line_more(LIST_SEP)
                self.line_term()
            if JAVA_STYLE_LIST_DEDENT:
                self.dec_margin()
                self.line_init()
            else:
                self.line_init()
                self.dec_margin()
        else:
            for node in (self.nodes)[:1]:
                node.put(can_split=True)
            self.line_more(LIST_SEP, can_split_after=True)
            for node in (self.nodes)[1:2]:
                node.put(can_split=True)
            for node in (self.nodes)[2:]:
                self.line_more(LIST_SEP, can_split_after=True)
                node.put(can_split=True)
        self.line_more(']', tab_clear=True)
        return self

    #@+node:ekr.20141010141310.18747: *5* make_local_name
    def make_local_name(self):
        for node in self.nodes:
            node.make_local_name()
        return self

    #@+node:ekr.20141010141310.18748: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.nodes[-1].get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18749: *4* class NodeAsgName
class NodeAsgName(Node):

    """Destination of an assignment operation.

    """

    tag = 'AsgName'

    #@+others
    #@+node:ekr.20141010141310.18750: *5* __init__
    def __init__(self, indent, lineno, name, flags):
        Node.__init__(self, indent, lineno)
        self.name = transform(indent, lineno, name)
        self.flags = transform(indent, lineno, flags)
        return 

    #@+node:ekr.20141010141310.18751: *5* put
    def put(self, can_split=False):
        is_del = self.flags.get_as_str() in ['OP_DELETE']
        if is_del:
            self.line_init()
            self.line_more('del ')
        self.line_more(NAME_SPACE.get_name(self.name))
        if DEBUG:
            self.line_more(' /* AsgName flags:  ')
            self.flags.put()
            self.line_more(' */ ')
        if is_del:
            self.line_term()
        return self

    #@+node:ekr.20141010141310.18752: *5* make_local_name
    def make_local_name(self):
        if NAME_SPACE.has_name(self.name):
            pass
        else:
            NAME_SPACE.make_local_name(self.name)
        return self

    #@+node:ekr.20141010141310.18753: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.name.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18754: *4* class NodeAsgTuple
class NodeAsgTuple(Node):

    """A tuple as a destination of an assignment operation.

    """

    tag = 'AsgTuple'

    #@+others
    #@+node:ekr.20141010141310.18755: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return 

    #@+node:ekr.20141010141310.18756: *5* put
    def put(self, can_split=False, is_paren_required=True):
        # pylint: disable=arguments-differ
        if len(self.nodes) > MAX_SEPS_SERIES:
            self.line_more('(', tab_set=True)
            self.line_term()
            self.inc_margin()
            for node in self.nodes:
                self.line_init()
                node.put(can_split=True)
                self.line_more(LIST_SEP)
                self.line_term()
            if JAVA_STYLE_LIST_DEDENT:
                self.dec_margin()
                self.line_init()
            else:
                self.line_init()
                self.dec_margin()
            self.line_more(')', tab_clear=True)
        elif is_paren_required or PARENTHESIZE_TUPLE_DISPLAY:
            self.line_more('(', tab_set=True)
            for node in (self.nodes)[:1]:
                node.put(can_split=True)
                self.line_more(LIST_SEP, can_split_after=True)
            for node in (self.nodes)[1:2]:
                node.put(can_split=True)
            for node in (self.nodes)[2:]:
                self.line_more(LIST_SEP, can_split_after=True)
                node.put(can_split=True)
            self.line_more(')', tab_clear=True)
        else:
            for node in (self.nodes)[:1]:
                node.put()
                self.line_more(LIST_SEP, can_break_after=True)
            for node in (self.nodes)[1:2]:
                node.put()
            for node in (self.nodes)[2:]:
                self.line_more(LIST_SEP, can_break_after=True)
                node.put()
        return self

    #@+node:ekr.20141010141310.18757: *5* make_local_name
    def make_local_name(self):
        for node in self.nodes:
            node.make_local_name()
        return self

    #@+node:ekr.20141010141310.18758: *5* get_hi_lineno
    def get_hi_lineno(self):
        return (self.nodes)[-1].get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18759: *4* class NodeAssert
class NodeAssert(Node):

    """Assertion.

    """

    tag = 'Assert'

    #@+others
    #@+node:ekr.20141010141310.18760: *5* __init__
    def __init__(self, indent, lineno, test, fail):
        Node.__init__(self, indent, lineno)
        self.test = transform(indent, lineno, test)
        self.fail = transform(indent, lineno, fail)
        return 

    #@+node:ekr.20141010141310.18761: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('assert ')
        self.test.put(can_split=can_split)
        if self.fail is None:
            pass
        else:
            self.line_more(LIST_SEP, can_break_after=True)
            self.fail.put()
        self.line_term()
        return self

    #@+node:ekr.20141010141310.18762: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = self.test.get_hi_lineno()
        if self.fail is None:
            pass
        else:
            lineno = self.fail.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18763: *4* class NodeAssign
class NodeAssign(Node):

    """Set one or more destinations to the value of the expression.

    """

    tag = 'Assign'

    #@+others
    #@+node:ekr.20141010141310.18764: *5* __init__
    def __init__(self, indent, lineno, nodes, expr):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        self.expr = transform(indent, lineno, expr)
        return 

    #@+node:ekr.20141010141310.18765: *5* put
    def put(self, can_split=False):
        self.line_init()
        for node in self.nodes:
            if isinstance(node, NodeAsgTuple):
                node.put(can_split=can_split, is_paren_required=False)
            else:
                node.put(can_split=can_split)
            self.line_more(ASSIGNMENT, can_break_after=True)
        if isinstance(self.expr, NodeYield):
            self.line_more('(')
            self.expr.put(can_split=True)
            self.line_more(')')
        elif isinstance(self.expr, NodeTuple):
            self.expr.put(can_split=can_split, is_paren_required=False)
        else:
            self.expr.put(can_split=can_split)
        self.line_term()
        return self

    #@+node:ekr.20141010141310.18766: *5* marshal_names
    def marshal_names(self):
        for node in self.nodes:
            node.make_local_name()
        return self

    #@+node:ekr.20141010141310.18767: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18768: *4* class NodeAugAssign
class NodeAugAssign(Node):

    """Augment the destination by the value of the expression.

    """

    tag = 'AugAssign'

    #@+others
    #@+node:ekr.20141010141310.18769: *5* __init__
    def __init__(self, indent, lineno, node, op, expr):
        Node.__init__(self, indent, lineno)
        self.node = transform(indent, lineno, node)
        self.op = transform(indent, lineno, op)
        self.expr = transform(indent, lineno, expr)
        return 

    #@+node:ekr.20141010141310.18770: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.node.put(can_split=can_split)
        op = ASSIGNMENT.replace('=', self.op.get_as_str())
        self.line_more(op, can_break_after=True)
        self.expr.put(can_split=can_split)
        self.line_term()
        return self

    #@+node:ekr.20141010141310.18771: *5* marshal_names
    def marshal_names(self):
        self.node.make_local_name()
        return self

    #@+node:ekr.20141010141310.18772: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18773: *4* class NodeBackquote
class NodeBackquote(Node):

    """String conversion a'la *repr*.

    """

    tag = 'Backquote'

    #@+others
    #@+node:ekr.20141010141310.18774: *5* __init__
    def __init__(self, indent, lineno, expr):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        return

    #@+node:ekr.20141010141310.18775: *5* put
    def put(self, can_split=False):
        self.line_more('`')
        self.expr.put(can_split=can_split)
        self.line_more('`')
        return self

    #@+node:ekr.20141010141310.18776: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18777: *4* class NodeBitAnd
class NodeBitAnd(NodeOprAssoc):

    '''Bitwise "and" operation (set union).

    '''

    tag = 'BitAnd'

    #@+others
    #@+node:ekr.20141010141310.18778: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return

    #@+node:ekr.20141010141310.18779: *5* put
    def put(self, can_split=False):
        for node in (self.nodes)[:1]:
            self.put_expr(node, can_split=can_split)
        for node in (self.nodes)[1:]:
            self.line_more(' ', can_split_after=can_split, can_break_after=True)
            self.line_more('& ')
            self.put_expr(node, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18780: *5* get_hi_lineno
    def get_hi_lineno(self):
        return (self.nodes)[-1].get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18781: *4* class NodeBitOr
class NodeBitOr(NodeOprAssoc):

    '''Bitwise "or" operation (set intersection).

    '''

    tag = 'BitOr'

    #@+others
    #@+node:ekr.20141010141310.18782: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return 

    #@+node:ekr.20141010141310.18783: *5* put
    def put(self, can_split=False):
        for node in (self.nodes)[:1]:
            self.put_expr(node, can_split=can_split)
        for node in (self.nodes)[1:]:
            self.line_more(' ', can_split_after=can_split, can_break_after=True)
            self.line_more('| ')
            self.put_expr(node, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18784: *5* get_hi_lineno
    def get_hi_lineno(self):
        return (self.nodes)[-1].get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18785: *4* class NodeBitXor
class NodeBitXor(NodeOprAssoc):

    '''Bitwise "xor" operation.

    '''

    tag = 'BitXor'

    #@+others
    #@+node:ekr.20141010141310.18786: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return 

    #@+node:ekr.20141010141310.18787: *5* put
    def put(self, can_split=False):
        for node in (self.nodes)[:1]:
            self.put_expr(node, can_split=can_split)
        for node in (self.nodes)[1:]:
            self.line_more(' ', can_split_after=can_split, can_break_after=True)
            self.line_more('^ ')
            self.put_expr(node, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18788: *5* get_hi_lineno
    def get_hi_lineno(self):
        return (self.nodes)[-1].get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18789: *4* class NodeBreak
class NodeBreak(Node):

    """Escape from a loop.

    """

    tag = 'Break'

    #@+others
    #@+node:ekr.20141010141310.18790: *5* __init__
    def __init__(self, indent, lineno):
        Node.__init__(self, indent, lineno)
        return 

    #@+node:ekr.20141010141310.18791: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('break')
        self.line_term()
        return self


    #@-others
#@+node:ekr.20141010141310.18792: *4* class NodeCallFunc
class NodeCallFunc(Node):

    """Function invocation.

    """

    tag = 'CallFunc'

    #@+others
    #@+node:ekr.20141010141310.18793: *5* __init__
    def __init__(self, indent, lineno, node, args, star_args, dstar_args):
        Node.__init__(self, indent, lineno)
        self.node = transform(indent, lineno, node)
        self.args = [transform(indent, lineno, arg) for arg in args]
        self.star_args = transform(indent, lineno, star_args)
        self.dstar_args = transform(indent, lineno, dstar_args)
        if len(self.args) == 1:
            arg = (self.args)[0]
            if isinstance(arg, NodeGenExpr):
                arg.need_parens = False
        return 

    #@+node:ekr.20141010141310.18794: *5* put
    def put(self, can_split=False):

        def count_seps():
            result = len(self.args)
            if self.star_args is None:
                pass
            else:
                result += 1
            if self.dstar_args is None:
                pass
            else:
                result += 1
            return result

        if isinstance(self.node, NodeLambda):
            self.line_more('(')
            self.node.put(can_split=True)
            self.line_more(')')
        else:
            self.node.put(can_split=can_split)
        self.line_more('(', tab_set=True)
        if count_seps() > MAX_SEPS_FUNC_REF:
            self.line_term()
            self.inc_margin()
            arg_list = [('', arg) for arg in self.args]
            has_stars = False
            if self.star_args is None:
                pass
            else:
                arg_list.append(('*', self.star_args))
                has_stars = True
            if self.dstar_args is None:
                pass
            else:
                arg_list.append(('**', self.dstar_args))
                has_stars = True
            for (sentinel, arg) in arg_list[:-1]:
                self.line_init()
                self.line_more(sentinel)
                arg.put(can_split=True)
                self.line_more(LIST_SEP)
                self.line_term()
            for (sentinel, arg) in arg_list[-1:]:
                self.line_init()
                self.line_more(sentinel)
                arg.put(can_split=True)
                if has_stars:
                    pass
                else:
                    self.line_more(LIST_SEP)
                self.line_term()
            if JAVA_STYLE_LIST_DEDENT:
                self.dec_margin()
                self.line_init()
            else:
                self.line_init()
                self.dec_margin()
        else:
            for arg in (self.args)[:-1]:
                arg.put(can_split=True)
                self.line_more(FUNCTION_PARAM_SEP, can_split_after=True)
            for arg in (self.args)[-1:]:
                arg.put(can_split=True)
                if self.star_args is None and self.dstar_args is None:
                    pass
                else:
                    self.line_more(FUNCTION_PARAM_SEP, can_split_after=True)
            if self.star_args is None:
                pass
            else:
                self.line_more('*')
                self.star_args.put(can_split=True)
                if self.dstar_args is None:
                    pass
                else:
                    self.line_more(FUNCTION_PARAM_SEP, can_split_after=True)
            if self.dstar_args is None:
                pass
            else:
                self.line_more('**')
                self.dstar_args.put(can_split=True)
        self.line_more(')', tab_clear=True)
        return self

    #@+node:ekr.20141010141310.18795: *5* get_lineno
    def get_lineno(self):
        return self.node.get_lineno()

    #@+node:ekr.20141010141310.18796: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = Node.get_hi_lineno(self)
        if self.args:
            lineno = (self.args)[-1].get_hi_lineno()
        if self.star_args is None:
            pass
        else:
            lineno = self.star_args.get_hi_lineno()
        if self.dstar_args is None:
            pass
        else:
            lineno = self.dstar_args.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18797: *4* class NodeClass
class NodeClass(Node):

    """Class declaration.

    """

    tag = 'Class'

    #@+others
    #@+node:ekr.20141010141310.18798: *5* __init__
    def __init__(self, indent, lineno, name, bases, doc, code):
        Node.__init__(self, indent, lineno)
        self.name = transform(indent, lineno, name)
        self.bases = [transform(indent, lineno, base) for base in bases]
        self.doc = transform(indent + 1, lineno, doc)
        self.code = transform(indent + 1, lineno, code)
        return 

    #@+node:ekr.20141010141310.18799: *5* put
    def put(self, can_split=False):
        if is_leo:
            spacing = 1
        elif NAME_SPACE.is_global():
            spacing = 2
        else:
            spacing = 1
        self.line_init(need_blank_line=spacing)
        self.line_more('class ')
        self.line_more(NAME_SPACE.get_name(self.name))
        if self.bases:
            self.line_more('(')
            for base in (self.bases)[:1]:
                base.put(can_split=True)
            for base in (self.bases)[1:]:
                self.line_more(LIST_SEP, can_split_after=True)
                base.put(can_split=True)
            self.line_more(')')
        self.line_more(':')
        self.line_term(self.code.get_lineno() - 1)
        if self.doc is None:
            pass
        else:
            self.doc.put_doc(need_blank_line=1)
        OUTPUT.put_blank_line(6)
        self.push_scope()
        self.code.marshal_names()
        self.code.put()
        self.pop_scope()
        OUTPUT.put_blank_line(7, count=spacing)
        return self

    #@+node:ekr.20141010141310.18800: *5* push_scope
    def push_scope(self):
        NAME_SPACE.push_scope()
        return self

    #@+node:ekr.20141010141310.18801: *5* pop_scope
    def pop_scope(self):
        NAME_SPACE.pop_scope()
        return self

    #@+node:ekr.20141010141310.18802: *5* marshal_names
    def marshal_names(self):
        NAME_SPACE.make_class_name(self.name)
        return self

    #@+node:ekr.20141010141310.18803: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = self.name.get_hi_lineno()
        if self.bases:
            lineno = (self.bases)[-1].get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18804: *4* class NodeCompare
class NodeCompare(NodeOprNotAssoc):

    """Logical comparison.

    """

    tag = 'Compare'

    #@+others
    #@+node:ekr.20141010141310.18805: *5* __init__
    def __init__(self, indent, lineno, expr, ops):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        self.ops = [(op, transform(indent, lineno, ex)) for (op, ex) in 
                    ops]
        return 

    #@+node:ekr.20141010141310.18806: *5* put
    def put(self, can_split=False):
        self.put_expr(self.expr, can_split=can_split)
        for (op, ex) in self.ops:
            self.line_more(' ', can_split_after=can_split, can_break_after=True)
            self.line_more('%s ' % op)
            self.put_expr(ex, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18807: *5* get_hi_lineno
    def get_hi_lineno(self):
        (op, ex) = (self.ops)[-1]
        return ex.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18808: *4* class NodeConst
class NodeConst(Node):

    """Literal or expression.

    """

    tag = 'Const'

    #@+others
    #@+node:ekr.20141010141310.18809: *5* __init__
    def __init__(self, indent, lineno, value):
        Node.__init__(self, indent, lineno)
        self.value = transform(indent, lineno, value)
        return 

    #@+node:ekr.20141010141310.18810: *5* put
    def put(self, can_split=False):
        if self.is_str():
            self.value.put_lit(can_split=can_split)
        elif isinstance(self.value, Node):
            self.value.put(can_split=can_split)
        else:
            self.line_more(self.get_as_repr())
        return self

    #@+node:ekr.20141010141310.18811: *5* is_none
    def is_none(self):
        return self.value is None

    #@+node:ekr.20141010141310.18812: *5* is_str
    def is_str(self):
        return isinstance(self.value, NodeStr)

    #@+node:ekr.20141010141310.18813: *5* get_as_repr
    def get_as_repr(self):
        original_values = COMMENTS.literal_pool.get(repr(self.value), [])
        if len(original_values) == 1:
            (result, lineno) = original_values[0]
        else:
            result = repr(self.value)
        return result


    #@-others
#@+node:ekr.20141010141310.18814: *4* class NodeContinue
class NodeContinue(Node):

    """Start a new trip through a loop.

    """

    tag = 'Continue'

    #@+others
    #@+node:ekr.20141010141310.18815: *5* __init__
    def __init__(self, indent, lineno):
        Node.__init__(self, indent, lineno)
        return 

    #@+node:ekr.20141010141310.18816: *5* put
    def put(self, can_split=False):
        # pylint: disable=arguments-differ
        self.line_init()
        self.line_more('continue')
        self.line_term()
        return self


    #@-others
#@+node:ekr.20141010141310.18817: *4* class NodeDecorators
class NodeDecorators(Node):

    """Functions that take a class method (the next) and a return
    callable object, e.g., *classmethod*.

    """
    #@+others
    #@+node:ekr.20141010141310.18818: *5* __init__

    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return 

    #@+node:ekr.20141010141310.18819: *5* put
    def put(self, spacing=0, can_split=False):
        # pylint: disable=arguments-differ
        for node in self.nodes:
            self.line_init(need_blank_line=spacing)
            self.line_more('@')
            node.put(can_split=can_split)
            self.line_term()
            spacing = 0
        return self

    #@+node:ekr.20141010141310.18820: *5* get_hi_lineno
    def get_hi_lineno(self):
        return (self.nodes)[-1].get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18821: *4* class NodeDict
class NodeDict(Node):

    """Declaration of a map (dictionary).

    """

    tag = 'Dict'

    #@+others
    #@+node:ekr.20141010141310.18822: *5* __init__
    def __init__(self, indent, lineno, items):
        Node.__init__(self, indent, lineno)
        self.items = [(transform(indent, lineno, key), transform(indent, 
                      lineno, value)) for (key, value) in items]
        return

    #@+node:ekr.20141010141310.18823: *5* put
    def put(self, can_split=False):

        def put_item():
            key.put(can_split=False)
            self.line_more(DICT_COLON)
            value.put(can_split=can_split)
            return 

        self.line_more('{', tab_set=True)
        if len(self.items) > MAX_SEPS_DICT:
            self.line_term()
            self.inc_margin()
            for (key, value) in self.items:
                self.line_init()
                put_item()
                self.line_more(LIST_SEP)
                self.line_term()
            if JAVA_STYLE_LIST_DEDENT:
                self.dec_margin()
                self.line_init()
            else:
                self.line_init()
                self.dec_margin()
        else:
            for (key, value) in (self.items)[:1]:
                put_item()
            for (key, value) in (self.items)[1:]:
                self.line_more(LIST_SEP, can_split_after=True)
                put_item()
        self.line_more('}', tab_clear=True)
        return self

    #@+node:ekr.20141010141310.18824: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = Node.get_hi_lineno(self)
        if self.items:
            (key, value) = (self.items)[-1]
            lineno = value.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18825: *4* class NodeDiscard
class NodeDiscard(Node):

    """Evaluate an expression (function) without saving the result.

    """

    tag = 'Discard'

    #@+others
    #@+node:ekr.20141010141310.18826: *5* __init__
    def __init__(self, indent, lineno, expr):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        return 

    #@+node:ekr.20141010141310.18827: *5* put
    def put(self, can_split=False):
        if isinstance(self.expr, NodeConst) and (not KEEP_UNASSIGNED_CONSTANTS):
            pass
        else:
            self.line_init()
            self.expr.put(can_split=can_split)
            self.line_term()
        return self

    #@+node:ekr.20141010141310.18828: *5* marshal_names
    def marshal_names(self):
        self.expr.marshal_names()
        return self

    #@+node:ekr.20141010141310.18829: *5* get_lineno
    def get_lineno(self):
        return self.expr.get_lineno()

    #@+node:ekr.20141010141310.18830: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18831: *4* class NodeDiv
class NodeDiv(NodeOprLeftAssoc):

    """Division operation.

    """

    tag = 'Div'

    #@+others
    #@+node:ekr.20141010141310.18832: *5* __init__
    def __init__(self, indent, lineno, left, right):
        Node.__init__(self, indent, lineno)
        self.left = transform(indent, lineno, left)
        self.right = transform(indent, lineno, right)
        return 

    #@+node:ekr.20141010141310.18833: *5* put
    def put(self, can_split=False):
        self.put_expr(self.left, can_split=can_split, pos='left')
        self.line_more(' ', can_split_after=can_split, can_break_after=True)
        self.line_more('/ ')
        self.put_expr(self.right, can_split=can_split, pos='right')
        return self

    #@+node:ekr.20141010141310.18834: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.right.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18835: *4* class NodeEllipsis
class NodeEllipsis(Node):

    tag = 'Ellipsis'

    #@+others
    #@+node:ekr.20141010141310.18836: *5* __init__
    def __init__(self, indent, lineno):
        Node.__init__(self, indent, lineno)
        return

    #@+node:ekr.20141010141310.18837: *5* put
    def put(self, can_split=False):
        self.line_more('...')
        return self


    #@-others
#@+node:ekr.20141010141310.18838: *4* class NodeExec
class NodeExec(Node):

    """Execute a given string of Python code in a specified namespace.

    """

    tag = 'Exec'

    #@+others
    #@+node:ekr.20141010141310.18839: *5* __init__
    def __init__(self, indent, lineno, expr, locals, globals):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        self.locals = transform(indent, lineno, locals)
        self.globals = transform(indent, lineno, globals)
        return 

    #@+node:ekr.20141010141310.18840: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('exec ')
        self.expr.put(can_split=can_split)
        if self.locals is None:
            pass
        else:
            self.line_more(' in ', can_break_after=True)
            self.locals.put(can_split=can_split)
            if self.globals is None:
                pass
            else:
                self.line_more(LIST_SEP, can_break_after=True)
                self.globals.put(can_split=can_split)
        self.line_term()
        return self

    #@+node:ekr.20141010141310.18841: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = self.expr.get_hi_lineno()
        if self.locals is None:
            pass
        else:
            lineno = self.locals.get_hi_lineno()
            if self.globals is None:
                pass
            else:
                lineno = self.globals.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18842: *4* class NodeFor
class NodeFor(Node):

    """For loop.

    """

    tag = 'For'

    #@+others
    #@+node:ekr.20141010141310.18843: *5* __init__
    def __init__(self, indent, lineno, assign, list, body, else_):
        Node.__init__(self, indent, lineno)
        self.assign = transform(indent, lineno, assign)
        self.list = transform(indent, lineno, list)
        self.body = transform(indent + 1, lineno, body)
        self.else_ = transform(indent + 1, lineno, else_)
        return 

    #@+node:ekr.20141010141310.18844: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('for ')
        if isinstance(self.assign, NodeAsgTuple):
            self.assign.put(can_split=can_split, is_paren_required=False)
        else:
            self.assign.put(can_split=can_split)
        self.line_more(' in ', can_break_after=True)
        if isinstance(self.list, NodeTuple):
            self.list.put(can_split=can_split, is_paren_required=False)
        else:
            self.list.put(can_split=can_split)
        self.line_more(':')
        self.line_term(self.body.get_lineno() - 1)
        self.body.put()
        if self.else_ is None:
            pass
        else:
            self.line_init()
            self.line_more('else:')
            self.line_term(self.else_.get_lineno() - 1)
            self.else_.put()
        return self

    #@+node:ekr.20141010141310.18845: *5* marshal_names
    def marshal_names(self):
        self.assign.make_local_name()
        self.body.marshal_names()
        if self.else_ is None:
            pass
        else:
            self.else_.marshal_names()
        return self

    #@+node:ekr.20141010141310.18846: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.list.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18847: *4* class NodeFloorDiv
class NodeFloorDiv(NodeOprLeftAssoc):

    """Floor division operation.

    """

    tag = 'FloorDiv'


    #@+others
    #@+node:ekr.20141010141310.18848: *5* __init__
    def __init__(self, indent, lineno, left, right):
        Node.__init__(self, indent, lineno)
        self.left = transform(indent, lineno, left)
        self.right = transform(indent, lineno, right)
        return 

    #@+node:ekr.20141010141310.18849: *5* put
    def put(self, can_split=False):
        self.put_expr(self.left, can_split=can_split, pos='left')
        self.line_more(' ', can_split_after=can_split, can_break_after=True)
        self.line_more('// ')
        self.put_expr(self.right, can_split=can_split, pos='right')
        return self

    #@+node:ekr.20141010141310.18850: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.right.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18851: *4* class NodeFrom
class NodeFrom(Node):

    """Import a name space.

    """

    tag = 'From'

    #@+others
    #@+node:ekr.20141010141310.18852: *5* __init__
    def __init__(self, indent, lineno, modname, names):
        Node.__init__(self, indent, lineno)
        self.modname = transform(indent, lineno, modname)
        self.names = [(transform(indent, lineno, identifier), transform(indent, 
                      lineno, name)) for (identifier, name) in names]
        return 

    #@+node:ekr.20141010141310.18853: *5* put
    def put(self, can_split=False):

        def put_name():
            identifier.put(can_split=can_split)
            if name is None:
                pass
            else:
                self.line_more(' as ')
                name.put(can_split=can_split)
            return 

        self.line_init()
        self.line_more('from ')
        self.modname.put(can_split=can_split)
        self.line_more(' import ')
        for (identifier, name) in (self.names)[:-1]:
            put_name()
            self.line_more(LIST_SEP, can_break_after=True)
        for (identifier, name) in (self.names)[-1:]:
            put_name()
        self.line_term()
        return self

    #@+node:ekr.20141010141310.18854: *5* marshal_names
    def marshal_names(self):
        for (identifier, name) in self.names:
            if name is None:
                NAME_SPACE.make_imported_name(identifier)
            else:
                NAME_SPACE.make_local_name(name)
        return self

    #@+node:ekr.20141010141310.18855: *5* get_hi_lineno
    def get_hi_lineno(self):
        (identifier, name) = (self.names)[-1]
        lineno = identifier.get_hi_lineno()
        if name is None:
            pass
        else:
            lineno = name.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18856: *4* class NodeFunction
class NodeFunction(Node):

    """Function declaration.

    """

    tag = 'Function'

    #@+others
    #@+node:ekr.20141010141310.18857: *5* __init__
    def __init__(
        self,
        indent,
        lineno,
        decorators,
        name,
        argnames,
        defaults,
        flags,
        doc,
        code,
        ):

        Node.__init__(self, indent, lineno)
        self.decorators = transform(indent, lineno, decorators)
        self.name = transform(indent, lineno, name)
        self.argnames = self.walk(argnames, self.xform)
        self.defaults = [transform(indent, lineno, default) for default in
                         defaults]
        self.flags = transform(indent, lineno, flags)
        self.doc = transform(indent + 1, lineno, doc)
        self.code = transform(indent + 1, lineno, code)
        return

    #@+node:ekr.20141010141310.18858: *5* walk
    def walk(self, tuple_, func, need_tuple=False):
        if isinstance(tuple_, tuple) or isinstance(tuple_, list):
            result = [self.walk(item, func, need_tuple) for item in
                      tuple_]
            if need_tuple:
                result = tuple(result)
        else:
            result = func(tuple_)
        return result

    #@+node:ekr.20141010141310.18859: *5* xform
    def xform(self, node):
        result = transform(self.indent, self.lineno, node)
        return result

    #@+node:ekr.20141010141310.18860: *5* pair_up
    def pair_up(self, args, defaults):
        args = args[:]          # This function manipulates its arguments
        defaults = defaults[:]  # destructively, so make copies first.
        stars = []
        args.reverse()
        defaults.reverse()
        is_excess_positionals = self.flags.int & 4
        is_excess_keywords = self.flags.int & 8
        if is_excess_positionals == 0:
            pass
        else:
            stars.insert(0, '*')
            defaults.insert(0, None)
        if is_excess_keywords == 0:
            pass
        else:
            stars.insert(0, '**')
            defaults.insert(0, None)
        result = map(None, args, defaults, stars)
        result.reverse()
        return result

    #@+node:ekr.20141010141310.18861: *5* put_parm
    def put_parm(self, arg, default, stars, can_split=True):
        if stars is None:
            pass
        else:
            self.line_more(stars)
        tuple_ = self.walk(arg, NAME_SPACE.get_name, need_tuple=True)
        tuple_ = str(tuple_)
        tuple_ = tuple_.replace("'", '').replace(',)', ', )')
        self.line_more(tuple_)
        if default is None:
            pass
        else:
            self.line_more(FUNCTION_PARAM_ASSIGNMENT)
            default.put(can_split=can_split)
        return

    #@+node:ekr.20141010141310.18862: *5* put
    def put(self, can_split=False):
        if is_leo:
            spacing = 1
        elif NAME_SPACE.is_global():
            spacing = 2
        else:
            spacing = 1
        if self.decorators is None:
            pass
        else:
            self.decorators.put(spacing)
            spacing = 0
        self.line_init(need_blank_line=spacing)
        self.line_more('def ')
        self.line_more(NAME_SPACE.get_name(self.name))
        self.push_scope()
        parms = self.pair_up(self.argnames, self.defaults)
        for (arg, default, stars) in parms:
            self.walk(arg, NAME_SPACE.make_formal_param_name)
        self.code.marshal_names()
        self.line_more('(', tab_set=True)
        if len(parms) > MAX_SEPS_FUNC_DEF:
            self.line_term()
            self.inc_margin()
            for (arg, default, stars) in parms[:-1]:
                self.line_init()
                self.put_parm(arg, default, stars)
                self.line_more(FUNCTION_PARAM_SEP)
                self.line_term()
            for (arg, default, stars) in parms[-1:]:
                self.line_init()
                self.put_parm(arg, default, stars)
                if stars is None:
                    self.line_more(FUNCTION_PARAM_SEP)
                self.line_term()
            if JAVA_STYLE_LIST_DEDENT:
                self.dec_margin()
                self.line_init()
            else:
                self.line_init()
                self.dec_margin()
        else:
            for (arg, default, stars) in parms[:1]:
                self.put_parm(arg, default, stars)
            for (arg, default, stars) in parms[1:]:
                self.line_more(FUNCTION_PARAM_SEP, can_split_after=True)
                self.put_parm(arg, default, stars)
        self.line_more('):', tab_clear=True)
        if DEBUG:
            self.line_more(' /* Function flags:  ')
            self.flags.put()
            self.line_more(' */ ')
        self.line_term(self.code.get_lineno() - 1)
        if self.doc is None:
            pass
        else:
            self.doc.put_doc()
        self.code.put()
        self.pop_scope()
        OUTPUT.put_blank_line(8, count=spacing)
        return self

    #@+node:ekr.20141010141310.18863: *5* push_scope
    def push_scope(self):
        NAME_SPACE.push_scope()
        return self

    #@+node:ekr.20141010141310.18864: *5* pop_scope
    def pop_scope(self):
        NAME_SPACE.pop_scope()
        return self

    #@+node:ekr.20141010141310.18865: *5* marshal_names
    def marshal_names(self):
        NAME_SPACE.make_function_name(self.name)
        return self


    #@-others
#@+node:ekr.20141010141310.18866: *4* class NodeLambda
class NodeLambda(NodeFunction):

    tag = 'Lambda'

    #@+others
    #@+node:ekr.20141010141310.18867: *5* __init__
    def __init__(self, indent, lineno, argnames, defaults, flags, code):
        NodeFunction.__init__(
            self,
            indent,
            lineno,
            None,
            None,
            argnames,
            defaults,
            flags,
            None,
            code,
            )
        return

    #@+node:ekr.20141010141310.18868: *5* put
    def put(self, can_split=False):
        self.line_more('lambda ')
        self.push_scope()
        parms = self.pair_up(self.argnames, self.defaults)
        for (arg, default, stars) in parms:
            self.walk(arg, NAME_SPACE.make_formal_param_name)
        for (arg, default, stars) in parms[:1]:
            self.put_parm(arg, default, stars, can_split=False)
        for (arg, default, stars) in parms[1:]:
            self.line_more(FUNCTION_PARAM_SEP, can_break_after=True)
            self.put_parm(arg, default, stars, can_split=False)
        self.line_more(': ', can_break_after=True)
        if DEBUG:
            self.line_more(' /* Function flags:  ')
            self.flags.put()
            self.line_more(' */ ')
        self.code.put()
        self.pop_scope()
        return self

    #@+node:ekr.20141010141310.18869: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.code.get_hi_lineno()

    #@+node:ekr.20141010141310.18870: *5* marshal_names
    def marshal_names(self):
        return self


    #@-others
#@+node:ekr.20141010141310.18871: *4* class NodeGenExpr
class NodeGenExpr(Node):

    """Generator expression, which needs its own parentheses.

    """

    tag = 'GenExpr'

    #@+others
    #@+node:ekr.20141010141310.18872: *5* __init__
    def __init__(self, indent, lineno, code):
        Node.__init__(self, indent, lineno)
        self.code = transform(indent, lineno, code)
        self.need_parens = True
        return 

    #@+node:ekr.20141010141310.18873: *5* put
    def put(self, can_split=False):
        if self.need_parens:
            self.line_more('(')
        self.code.put(can_split=True)
        if self.need_parens:
            self.line_more(')')
        return self

    #@+node:ekr.20141010141310.18874: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.code.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18875: *4* class NodeGenExprInner
class NodeGenExprInner(Node):

    """Generator expression inside parentheses.

    """

    tag = 'GenExprInner'

    #@+others
    #@+node:ekr.20141010141310.18876: *5* __init__
    def __init__(self, indent, lineno, expr, quals):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        self.quals = [transform(indent, lineno, qual) for qual in quals]
        return 

    #@+node:ekr.20141010141310.18877: *5* put
    def put(self, can_split=False):
        self.push_scope()
        self.marshal_names()
        self.expr.put(can_split=can_split)
        for qual in self.quals:
            qual.put(can_split=can_split)
        self.pop_scope()
        return self

    #@+node:ekr.20141010141310.18878: *5* push_scope
    def push_scope(self):
        NAME_SPACE.push_scope()
        return self

    #@+node:ekr.20141010141310.18879: *5* pop_scope
    def pop_scope(self):
        NAME_SPACE.pop_scope()
        return self

    #@+node:ekr.20141010141310.18880: *5* marshal_names
    def marshal_names(self):
        for qual in self.quals:
            qual.marshal_names()
        return self

    #@+node:ekr.20141010141310.18881: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = (self.quals)[-1].get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18882: *4* class NodeGenExprFor
class NodeGenExprFor(Node):

    '''"For" of a generator expression.

    '''

    tag = 'GenExprFor'

    #@+others
    #@+node:ekr.20141010141310.18883: *5* __init__
    def __init__(self, indent, lineno, assign, list, ifs):
        Node.__init__(self, indent, lineno)
        self.assign = transform(indent, lineno, assign)
        self.list = transform(indent, lineno, list)
        self.ifs = [transform(indent, lineno, if_) for if_ in ifs]
        return

    #@+node:ekr.20141010141310.18884: *5* put
    def put(self, can_split=False):
        self.line_more(' ', can_split_after=True)
        self.line_more('for ')
        self.assign.put(can_split=can_split)
        self.line_more(' in ', can_split_after=True)
        self.list.put(can_split=can_split)
        for if_ in self.ifs:
            if_.put(can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18885: *5* marshal_names
    def marshal_names(self):
        self.assign.make_local_name()
        return self

    #@+node:ekr.20141010141310.18886: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = self.list.get_hi_lineno()
        if self.ifs:
            lineno = (self.ifs)[-1].get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18887: *4* class NodeGenExprIf
class NodeGenExprIf(Node):

    '''"If" of a generator expression.

    '''

    tag = 'GenExprIf'

    #@+others
    #@+node:ekr.20141010141310.18888: *5* __init__
    def __init__(self, indent, lineno, test):
        Node.__init__(self, indent, lineno)
        self.test = transform(indent, lineno, test)
        return 

    #@+node:ekr.20141010141310.18889: *5* put
    def put(self, can_split=False):
        self.line_more(' ', can_split_after=True)
        self.line_more('if ')
        self.test.put(can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18890: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.test.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18891: *4* class NodeGetAttr
class NodeGetAttr(NodeOpr):

    """Class attribute (method).

    """

    tag = 'GetAttr'

    #@+others
    #@+node:ekr.20141010141310.18892: *5* __init__
    def __init__(self, indent, lineno, expr, attrname):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        self.attrname = transform(indent, lineno, attrname)
        return 

    #@+node:ekr.20141010141310.18893: *5* put
    def put(self, can_split=False):
        if isinstance(self.expr, NodeConst):
            if self.expr.is_str():
                self.expr.put()
            else:
                self.line_more('(')
                self.expr.put(can_split=True)
                self.line_more(')')
        else:
            self.put_expr(self.expr, can_split=can_split)
        self.line_more('.')
        self.line_more(NAME_SPACE.make_attr_name(self.expr, self.attrname))
        return self

    #@+node:ekr.20141010141310.18894: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.attrname.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18895: *4* class NodeGlobal
class NodeGlobal(Node):

    tag = 'Global'

    #@+others
    #@+node:ekr.20141010141310.18896: *5* __init__
    def __init__(self, indent, lineno, names):
        Node.__init__(self, indent, lineno)
        self.names = [transform(indent, lineno, name) for name in names]
        return 

    #@+node:ekr.20141010141310.18897: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('global ')
        for name in (self.names)[:1]:
            self.line_more(NAME_SPACE.get_name(name))
        for name in (self.names)[1:]:
            self.line_more(LIST_SEP, can_break_after=True)
            self.line_more(NAME_SPACE.get_name(name))
        self.line_term()
        return self

    #@+node:ekr.20141010141310.18898: *5* marshal_names
    def marshal_names(self):
        for name in self.names:
            NAME_SPACE.make_global_name(name)
        return self

    #@+node:ekr.20141010141310.18899: *5* get_hi_lineno
    def get_hi_lineno(self):
        return (self.names)[-1].get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18900: *4* class NodeIf
class NodeIf(Node):

    """True/False test.

    """

    tag = 'If'

    #@+others
    #@+node:ekr.20141010141310.18901: *5* __init__
    def __init__(self, indent, lineno, tests, else_):
        Node.__init__(self, indent, lineno)
        self.tests = [(transform(indent, lineno, expr), transform(indent +
                      1, lineno, stmt)) for (expr, stmt) in tests]
        self.else_ = transform(indent + 1, lineno, else_)
        return

    #@+node:ekr.20141010141310.18902: *5* put
    def put(self, can_split=False):
        for (expr, stmt) in (self.tests)[:1]:
            self.line_init()
            self.line_more('if ')
            expr.put(can_split=can_split)
            self.line_more(':')
            self.line_term(stmt.get_lineno() - 1)
            stmt.put()
        for (expr, stmt) in (self.tests)[1:]:
            self.line_init()
            self.line_more('elif ')
            expr.put(can_split=can_split)
            self.line_more(':')
            self.line_term(stmt.get_lineno() - 1)
            stmt.put()
        if self.else_ is None:
            pass
        else:
            self.line_init()
            self.line_more('else:')
            self.line_term(self.else_.get_lineno() - 1)
            self.else_.put()
        return self

    #@+node:ekr.20141010141310.18903: *5* marshal_names
    def marshal_names(self):
        for (expr, stmt) in self.tests:
            stmt.marshal_names()
        if self.else_ is None:
            pass
        else:
            self.else_.marshal_names()
        return self

    #@+node:ekr.20141010141310.18904: *5* get_hi_lineno
    def get_hi_lineno(self):
        (expr, stmt) = (self.tests)[0]
        return expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18905: *4* class NodeIfExp
class NodeIfExp(Node):

    """Conditional assignment.  (Ternary expression.)

    """

    tag = 'IfExp'

    #@+others
    #@+node:ekr.20141010141310.18906: *5* __init__
    def __init__(self, indent, lineno, test, then, else_):
        Node.__init__(self, indent, lineno)
        self.test = transform(indent, lineno, test)
        self.then = transform(indent, lineno, then)
        self.else_ = transform(indent, lineno, else_)
        return

    #@+node:ekr.20141010141310.18907: *5* put
    def put(self, can_split=False):
        self.line_more('(', tab_set=True)
        self.then.put(can_split=True)
        self.line_more(' if ')
        self.test.put(can_split=True)
        self.line_more(' else ')
        self.else_.put(can_split=True)
        self.line_more(')', tab_clear=True)
        return self

    #@+node:ekr.20141010141310.18908: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.else_.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18909: *4* class NodeImport
class NodeImport(Node):

    tag = 'Import'

    #@+others
    #@+node:ekr.20141010141310.18910: *5* __init__
    def __init__(self, indent, lineno, names):
        Node.__init__(self, indent, lineno)
        self.names = [(transform(indent, lineno, identifier), transform(indent,
                      lineno, name)) for (identifier, name) in names]
        return

    #@+node:ekr.20141010141310.18911: *5* put
    def put(self, can_split=False):

        def put_name():
            identifier.put(can_split=can_split)
            if name is None:
                pass
            else:
                self.line_more(' as ')
                name.put(can_split=can_split)
            return

        for (identifier, name) in self.names:
            self.line_init()
            self.line_more('import ')
            put_name()
            self.line_term()
        return self

    #@+node:ekr.20141010141310.18912: *5* marshal_names
    def marshal_names(self):
        for (identifier, name) in self.names:
            if name is None:
                pass
            else:
                NAME_SPACE.make_local_name(name)
        return self

    #@+node:ekr.20141010141310.18913: *5* get_hi_lineno
    def get_hi_lineno(self):
        (identifier, name) = (self.names)[-1]
        lineno = identifier.get_hi_lineno()
        if name is None:
            pass
        else:
            lineno = name.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18914: *4* class NodeInvert
class NodeInvert(NodeOpr):

    """Unary bitwise complement.

    """

    tag = 'Invert'

    #@+others
    #@+node:ekr.20141010141310.18915: *5* __init__
    def __init__(self, indent, lineno, expr):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        return 

    #@+node:ekr.20141010141310.18916: *5* put
    def put(self, can_split=False):
        self.line_more('~')
        self.put_expr(self.expr, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18917: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18918: *4* class NodeKeyword
class NodeKeyword(Node):

    """Formal parameter on a function invocation.

    """

    tag = 'Keyword'

    #@+others
    #@+node:ekr.20141010141310.18919: *5* __init__
    def __init__(self, indent, lineno, name, expr):
        Node.__init__(self, indent, lineno)
        self.name = transform(indent, lineno, name)
        self.expr = transform(indent, lineno, expr)
        return 

    #@+node:ekr.20141010141310.18920: *5* put
    def put(self, can_split=False):
        self.line_more(NAME_SPACE.make_keyword_name(self.name))
        self.line_more(FUNCTION_PARAM_ASSIGNMENT)
        self.expr.put(can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18921: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18922: *4* class NodeLeftShift
class NodeLeftShift(NodeOprLeftAssoc):

    """Bitwise shift left.

    """

    tag = 'LeftShift'


    #@+others
    #@+node:ekr.20141010141310.18923: *5* __init__
    def __init__(self, indent, lineno, left, right):
        Node.__init__(self, indent, lineno)
        self.left = transform(indent, lineno, left)
        self.right = transform(indent, lineno, right)
        return 

    #@+node:ekr.20141010141310.18924: *5* put
    def put(self, can_split=False):
        self.put_expr(self.left, can_split=can_split, pos='left')
        self.line_more(' ', can_split_after=can_split, can_break_after=True)
        self.line_more('<< ')
        self.put_expr(self.right, can_split=can_split, pos='right')
        return self

    #@+node:ekr.20141010141310.18925: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.right.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18926: *4* class NodeList
class NodeList(Node):

    """Declaration of a mutable list.

    """

    tag = 'List'

    #@+others
    #@+node:ekr.20141010141310.18927: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return 

    #@+node:ekr.20141010141310.18928: *5* put
    def put(self, can_split=False):
        self.line_more('[', tab_set=True)
        if len(self.nodes) > MAX_SEPS_SERIES:
            self.line_term()
            self.inc_margin()
            for node in self.nodes:
                self.line_init()
                node.put(can_split=True)
                self.line_more(LIST_SEP)
                self.line_term()
            if JAVA_STYLE_LIST_DEDENT:
                self.dec_margin()
                self.line_init()
            else:
                self.line_init()
                self.dec_margin()
        else:
            for node in (self.nodes)[:1]:
                node.put(can_split=True)
            for node in (self.nodes)[1:]:
                self.line_more(LIST_SEP, can_split_after=True)
                node.put(can_split=True)
        self.line_more(']', tab_clear=True)
        return self

    #@+node:ekr.20141010141310.18929: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = Node.get_hi_lineno(self)
        if self.nodes:
            lineno = (self.nodes)[-1].get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18930: *4* class NodeListComp
class NodeListComp(Node):

    """List comprehension.

    """

    tag = 'ListComp'

    #@+others
    #@+node:ekr.20141010141310.18931: *5* __init__
    def __init__(self, indent, lineno, expr, quals):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        self.quals = [transform(indent, lineno, qual) for qual in quals]
        return 

    #@+node:ekr.20141010141310.18932: *5* put
    def put(self, can_split=False):
        self.push_scope()
        self.marshal_names()
        self.line_more('[', tab_set=True)
        self.expr.put(can_split=True)
        for qual in self.quals:
            qual.put(can_split=True)
        self.line_more(']', tab_clear=True)
        self.pop_scope()
        return self

    #@+node:ekr.20141010141310.18933: *5* push_scope
    def push_scope(self):
        NAME_SPACE.push_scope()
        return self

    #@+node:ekr.20141010141310.18934: *5* pop_scope
    def pop_scope(self):
        NAME_SPACE.pop_scope()
        return self

    #@+node:ekr.20141010141310.18935: *5* marshal_names
    def marshal_names(self):
        for qual in self.quals:
            qual.marshal_names()
        return self

    #@+node:ekr.20141010141310.18936: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = (self.quals)[-1].get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18937: *4* class NodeListCompFor
class NodeListCompFor(Node):

    '''"For" of a list comprehension.

    '''

    tag = 'ListCompFor'

    #@+others
    #@+node:ekr.20141010141310.18938: *5* __init__
    def __init__(self, indent, lineno, assign, list, ifs):
        Node.__init__(self, indent, lineno)
        self.assign = transform(indent, lineno, assign)
        self.list = transform(indent, lineno, list)
        self.ifs = [transform(indent, lineno, if_) for if_ in ifs]
        return 

    #@+node:ekr.20141010141310.18939: *5* put
    def put(self, can_split=False):
        self.line_more(' ', can_split_after=True)
        self.line_more('for ')
        self.assign.put(can_split=can_split)
        self.line_more(' in ', can_split_after=True)
        self.list.put(can_split=can_split)
        for if_ in self.ifs:
            if_.put(can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18940: *5* marshal_names
    def marshal_names(self):
        self.assign.make_local_name()
        return self

    #@+node:ekr.20141010141310.18941: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = self.list.get_hi_lineno()
        if self.ifs:
            lineno = (self.ifs)[-1].get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18942: *4* class NodeListCompIf
class NodeListCompIf(Node):

    '''"If" of a list comprehension.

    '''

    tag = 'ListCompIf'

    #@+others
    #@+node:ekr.20141010141310.18943: *5* __init__
    def __init__(self, indent, lineno, test):
        Node.__init__(self, indent, lineno)
        self.test = transform(indent, lineno, test)
        return 

    #@+node:ekr.20141010141310.18944: *5* put
    def put(self, can_split=False):
        self.line_more(' ', can_split_after=True)
        self.line_more('if ')
        self.test.put(can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18945: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.test.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18946: *4* class NodeMod
class NodeMod(NodeOprLeftAssoc):

    """Modulus (string formatting) operation.

    """

    tag = 'Mod'

    #@+others
    #@+node:ekr.20141010141310.18947: *5* __init__
    def __init__(self, indent, lineno, left, right):
        Node.__init__(self, indent, lineno)
        self.left = transform(indent, lineno, left)
        self.right = transform(indent, lineno, right)
        return 

    #@+node:ekr.20141010141310.18948: *5* put
    def put(self, can_split=False):
        self.put_expr(self.left, can_split=can_split, pos='left')
        self.line_more(' ', can_split_after=can_split, can_break_after=True)
        self.line_more('% ')
        self.put_expr(self.right, can_split=can_split, pos='right')
        return self

    #@+node:ekr.20141010141310.18949: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.right.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18950: *4* class NodeModule
class NodeModule(Node):

    """A whole script.
    
    Contains a doc string and a statement.

    """

    tag = 'Module'

    #@+others
    #@+node:ekr.20141010141310.18951: *5* __init__
    def __init__(self, indent, lineno, doc, node):
        Node.__init__(self, indent, lineno)
        self.doc = transform(indent, lineno, doc)
        self.node = transform(indent, lineno, node)
        return 

    #@+node:ekr.20141010141310.18952: *5* put
    def put(self, can_split=False):
        if self.doc is None:
            pass
        else:
            self.doc.lineno = self.get_lineno()
            self.doc.put_doc()
        if BOILERPLATE == '':
            pass
        else:
            self.line_init()
            self.line_more(BOILERPLATE)
            self.line_term()
        self.node.put()
        return self

    #@+node:ekr.20141010141310.18953: *5* push_scope
    def push_scope(self):
        NAME_SPACE.push_scope()
        return self

    #@+node:ekr.20141010141310.18954: *5* pop_scope
    def pop_scope(self):
        NAME_SPACE.pop_scope()
        return self

    #@+node:ekr.20141010141310.18955: *5* marshal_names
    def marshal_names(self):
        self.node.marshal_names()
        return self

    #@+node:ekr.20141010141310.18956: *5* get_lineno
    def get_lineno(self):
        return self.node.get_lineno()


    #@-others
#@+node:ekr.20141010141310.18957: *4* class NodeMul
class NodeMul(NodeOprLeftAssoc):

    """Multiply operation.

    """

    tag = 'Mul'

    #@+others
    #@+node:ekr.20141010141310.18958: *5* __init__
    def __init__(self, indent, lineno, left, right):
        Node.__init__(self, indent, lineno)
        self.left = transform(indent, lineno, left)
        self.right = transform(indent, lineno, right)
        return 

    #@+node:ekr.20141010141310.18959: *5* put
    def put(self, can_split=False):
        self.put_expr(self.left, can_split=can_split, pos='left')
        self.line_more(' ', can_split_after=can_split, can_break_after=True)
        self.line_more('* ')
        self.put_expr(self.right, can_split=can_split, pos='right')
        return self

    #@+node:ekr.20141010141310.18960: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.right.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18961: *4* class NodeName
class NodeName(Node):

    """Variable.

    """

    tag = 'Name'

    #@+others
    #@+node:ekr.20141010141310.18962: *5* __init__
    def __init__(self, indent, lineno, name):
        Node.__init__(self, indent, lineno)
        self.name = transform(indent, lineno, name)
        return 

    #@+node:ekr.20141010141310.18963: *5* put
    def put(self, can_split=False):
        self.line_more(NAME_SPACE.get_name(self.name))
        return self

    #@+node:ekr.20141010141310.18964: *5* make_local_name
    def make_local_name(self):
        if NAME_SPACE.has_name(self.name):
            pass
        else:
            NAME_SPACE.make_local_name(self.name)
        return self

    #@+node:ekr.20141010141310.18965: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.name.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18966: *4* class NodeNot
class NodeNot(NodeOpr):

    """Logical negation.

    """

    tag = 'Not'

    #@+others
    #@+node:ekr.20141010141310.18967: *5* __init__
    def __init__(self, indent, lineno, expr):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        return 

    #@+node:ekr.20141010141310.18968: *5* put
    def put(self, can_split=False):
        self.line_more('not ')
        self.put_expr(self.expr, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18969: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18970: *4* class NodeOr
class NodeOr(NodeOprAssoc):

    '''Logical "or" operation.

    '''

    tag = 'Or'

    #@+others
    #@+node:ekr.20141010141310.18971: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return 

    #@+node:ekr.20141010141310.18972: *5* put
    def put(self, can_split=False):
        for node in (self.nodes)[:1]:
            self.put_expr(node, can_split=can_split)
        for node in (self.nodes)[1:]:
            self.line_more(' ', can_split_after=can_split, can_break_after=True)
            self.line_more('or ')
            self.put_expr(node, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.18973: *5* get_hi_lineno
    def get_hi_lineno(self):
        return (self.nodes)[-1].get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18974: *4* class NodePass
class NodePass(Node):

    """No-op.

    """

    tag = 'Pass'

    #@+others
    #@+node:ekr.20141010141310.18975: *5* __init__
    def __init__(self, indent, lineno):
        Node.__init__(self, indent, lineno)
        return 

    #@+node:ekr.20141010141310.18976: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('pass')
        self.line_term()
        return self


    #@-others
#@+node:ekr.20141010141310.18977: *4* class NodePower
class NodePower(NodeOprRightAssoc):

    """Exponentiation.

    """

    tag = 'Power'

    #@+others
    #@+node:ekr.20141010141310.18978: *5* __init__
    def __init__(self, indent, lineno, left, right):
        Node.__init__(self, indent, lineno)
        self.left = transform(indent, lineno, left)
        self.right = transform(indent, lineno, right)
        return 

    #@+node:ekr.20141010141310.18979: *5* put
    def put(self, can_split=False):
        self.put_expr(self.left, can_split=can_split, pos='left')
        self.line_more(' ', can_split_after=can_split, can_break_after=True)
        self.line_more('** ')
        self.put_expr(self.right, can_split=can_split, pos='right')
        return self

    #@+node:ekr.20141010141310.18980: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.right.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.18981: *4* class NodePrint
class NodePrint(Node):

    """The print statement with optional chevron and trailing comma.

    """

    tag = 'Print'

    #@+others
    #@+node:ekr.20141010141310.18982: *5* __init__
    def __init__(self, indent, lineno, nodes, dest):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        self.dest = transform(indent, lineno, dest)
        return 

    #@+node:ekr.20141010141310.18983: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('print ')
        if self.dest is None:
            pass
        else:
            self.line_more('>> ')
            self.dest.put(can_split=can_split)
            if self.nodes:
                self.line_more(LIST_SEP, can_break_after=True)
        for node in self.nodes:
            node.put(can_split=can_split)
            self.line_more(LIST_SEP, can_break_after=True)
        self.line_term()
        return self

    #@+node:ekr.20141010141310.18984: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = Node.get_hi_lineno(self)
        if self.dest is None:
            pass
        else:
            lineno = self.dest.get_hi_lineno()
        if self.nodes:
            lineno = (self.nodes)[-1].get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18985: *4* class NodePrintnl
class NodePrintnl(Node):

    """The print statement with optional chevron and without trailing comma.

    """

    tag = 'Printnl'

    #@+others
    #@+node:ekr.20141010141310.18986: *5* __init__
    def __init__(self, indent, lineno, nodes, dest):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        self.dest = transform(indent, lineno, dest)
        return 

    #@+node:ekr.20141010141310.18987: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('print ')
        if self.dest is None:
            pass
        else:
            self.line_more('>> ')
            self.dest.put(can_split=can_split)
            if self.nodes:
                self.line_more(LIST_SEP, can_break_after=True)
        for node in (self.nodes)[:-1]:
            node.put(can_split=can_split)
            self.line_more(LIST_SEP, can_break_after=True)
        for node in (self.nodes)[-1:]:
            node.put(can_split=can_split)
        self.line_term()
        return self

    #@+node:ekr.20141010141310.18988: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = Node.get_hi_lineno(self)
        if self.dest is None:
            pass
        else:
            lineno = self.dest.get_hi_lineno()
        if self.nodes:
            lineno = (self.nodes)[-1].get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18989: *4* class NodeRaise
class NodeRaise(Node):

    """Raise an exception.

    """

    tag = 'Raise'

    #@+others
    #@+node:ekr.20141010141310.18990: *5* __init__
    def __init__(self, indent, lineno, expr1, expr2, expr3):
        Node.__init__(self, indent, lineno)
        self.expr1 = transform(indent, lineno, expr1)
        self.expr2 = transform(indent, lineno, expr2)
        self.expr3 = transform(indent, lineno, expr3)
        return 

    #@+node:ekr.20141010141310.18991: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('raise ')
        if self.expr1 is None:
            pass
        else:
            self.expr1.put(can_split=can_split)
            if self.expr2 is None:
                pass
            else:
                self.line_more(LIST_SEP, can_break_after=True)
                self.expr2.put(can_split=can_split)
                if self.expr3 is None:
                    pass
                else:
                    self.line_more(LIST_SEP, can_break_after=True)
                    self.expr3.put(can_split=can_split)
        self.line_term()
        return self

    #@+node:ekr.20141010141310.18992: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = Node.get_hi_lineno(self)
        if self.expr1 is None:
            pass
        else:
            lineno = self.expr1.get_hi_lineno()
            if self.expr2 is None:
                pass
            else:
                lineno = self.expr2.get_hi_lineno()
                if self.expr3 is None:
                    pass
                else:
                    lineno = self.expr3.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18993: *4* class NodeReturn
class NodeReturn(Node):

    """Return a value from a function.

    """

    tag = 'Return'

    #@+others
    #@+node:ekr.20141010141310.18994: *5* __init__
    def __init__(self, indent, lineno, value):
        Node.__init__(self, indent, lineno)
        self.value = transform(indent, lineno, value)
        return 

    #@+node:ekr.20141010141310.18995: *5* has_value
    def has_value(self):
        return not (isinstance(self.value, NodeConst) and self.value.is_none())

    #@+node:ekr.20141010141310.18996: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('return ')
        if self.has_value():
            if isinstance(self.value, NodeTuple):
                self.value.put(can_split=can_split, is_paren_required=False)
            else:
                self.value.put(can_split=can_split)
        self.line_term()
        return self

    #@+node:ekr.20141010141310.18997: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = Node.get_hi_lineno(self)
        if self.has_value:
            lineno = self.value.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.18998: *4* class NodeRightShift
class NodeRightShift(NodeOprLeftAssoc):

    """Bitwise shift right.

    """

    tag = 'RightShift'

    #@+others
    #@+node:ekr.20141010141310.18999: *5* __init__
    def __init__(self, indent, lineno, left, right):
        Node.__init__(self, indent, lineno)
        self.left = transform(indent, lineno, left)
        self.right = transform(indent, lineno, right)
        return 

    #@+node:ekr.20141010141310.19000: *5* put
    def put(self, can_split=False):
        self.put_expr(self.left, can_split=can_split, pos='left')
        self.line_more(' ', can_split_after=can_split, can_break_after=True)
        self.line_more('>> ')
        self.put_expr(self.right, can_split=can_split, pos='right')
        return self

    #@+node:ekr.20141010141310.19001: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.right.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.19002: *4* class NodeSlice
class NodeSlice(NodeOpr):

    """A slice of a series.

    """

    tag = 'Slice'

    #@+others
    #@+node:ekr.20141010141310.19003: *5* __init__
    def __init__(self, indent, lineno, expr, flags, lower, upper):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        self.flags = transform(indent, lineno, flags)
        self.lower = transform(indent, lineno, lower)
        self.upper = transform(indent, lineno, upper)
        return 

    #@+node:ekr.20141010141310.19004: *5* has_value
    def has_value(self, node):
        return not (node is None or isinstance(node, NodeConst) and node.is_none())

    #@+node:ekr.20141010141310.19005: *5* put
    def put(self, can_split=False):
        is_del = self.flags.get_as_str() in ['OP_DELETE']
        if is_del:
            self.line_init()
            self.line_more('del ')
        if (isinstance(self.expr, NodeGetAttr)
            or isinstance(self.expr, NodeAsgAttr)):
            self.expr.put(can_split=can_split)
        else:
            self.put_expr(self.expr, can_split=can_split)
        self.line_more('[')
        if self.has_value(self.lower):
            self.lower.put(can_split=True)
        self.line_more(SLICE_COLON)
        if self.has_value(self.upper):
            self.upper.put(can_split=True)
        self.line_more(']')
        if DEBUG:
            self.line_more(' /* Subscript flags:  ')
            self.flags.put()
            self.line_more(' */ ')
        if is_del:
            self.line_term()
        return self

    #@+node:ekr.20141010141310.19006: *5* make_local_name
    def make_local_name(self):
        self.expr.make_local_name()
        return self

    #@+node:ekr.20141010141310.19007: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = Node.get_hi_lineno(self)
        if self.has_value(self.lower):
            lineno = self.lower.get_hi_lineno()
        if self.has_value(self.upper):
            lineno = self.upper.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.19008: *4* class NodeSliceobj
class NodeSliceobj(Node):

    """A subscript range.
    
    This is used for multi-dimensioned arrays.

    """

    tag = 'Sliceobj'

    #@+others
    #@+node:ekr.20141010141310.19009: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return 

    #@+node:ekr.20141010141310.19010: *5* has_value
    def has_value(self, node):
        return not (node is None or isinstance(node, NodeConst) and node.is_none())

    #@+node:ekr.20141010141310.19011: *5* put
    def put(self, can_split=False):
        for node in (self.nodes)[:1]:
            if self.has_value(node):
                node.put(can_split=can_split)
        for node in (self.nodes)[1:]:
            self.line_more(SLICE_COLON, can_split_after=True)
            if self.has_value(node):
                node.put(can_split=can_split)
        return self

    #@+node:ekr.20141010141310.19012: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = Node.get_hi_lineno(self)
        for node in self.nodes:
            if self.has_value(node):
                lineno = node.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.19013: *4* class NodeStmt
class NodeStmt(Node):

    """A list of nodes..

    """

    tag = 'Stmt'

    #@+others
    #@+node:ekr.20141010141310.19014: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return 

    #@+node:ekr.20141010141310.19015: *5* put
    def put(self, can_split=False):
        for node in self.nodes:
            node.put()
        return self

    #@+node:ekr.20141010141310.19016: *5* get_lineno
    def get_lineno(self):
        for node in self.nodes:
            result = node.get_lineno()
            if result == 0:
                pass
            else:
                return result
        return 0

    #@+node:ekr.20141010141310.19017: *5* marshal_names
    def marshal_names(self):
        for node in self.nodes:
            node.marshal_names()
        return self


    #@-others
#@+node:ekr.20141010141310.19018: *4* class NodeSub
class NodeSub(NodeOprLeftAssoc):

    """Subtract operation.

    """

    tag = 'Sub'

    #@+others
    #@+node:ekr.20141010141310.19019: *5* __init__
    def __init__(self, indent, lineno, left, right):
        Node.__init__(self, indent, lineno)
        self.left = transform(indent, lineno, left)
        self.right = transform(indent, lineno, right)
        return 

    #@+node:ekr.20141010141310.19020: *5* put
    def put(self, can_split=False):
        self.put_expr(self.left, can_split=can_split, pos='left')
        self.line_more(' ', can_split_after=can_split, can_break_after=True)
        self.line_more('- ')
        self.put_expr(self.right, can_split=can_split, pos='right')
        return self

    #@+node:ekr.20141010141310.19021: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.right.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.19022: *4* class NodeSubscript
class NodeSubscript(NodeOpr):

    """A subscripted sequence.

    """

    tag = 'Subscript'

    #@+others
    #@+node:ekr.20141010141310.19023: *5* __init__
    def __init__(self, indent, lineno, expr, flags, subs):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        self.flags = transform(indent, lineno, flags)
        self.subs = [transform(indent, lineno, sub) for sub in subs]
        return 

    #@+node:ekr.20141010141310.19024: *5* put
    def put(self, can_split=False):
        is_del = self.flags.get_as_str() in ['OP_DELETE']
        if is_del:
            self.line_init()
            self.line_more('del ')
        if (isinstance(self.expr, NodeGetAttr)
            or isinstance(self.expr, NodeAsgAttr)):
            self.expr.put(can_split=can_split)
        else:
            self.put_expr(self.expr, can_split=can_split)
        if DEBUG:
            self.line_more(' /* Subscript flags:  ')
            self.flags.put()
            self.line_more(' */ ')
        self.line_more('[', tab_set=True)
        for sub in (self.subs)[:1]:
            sub.put(can_split=True)
        for sub in (self.subs)[1:]:
            self.line_more(SUBSCRIPT_SEP, can_split_after=True)
            sub.put(can_split=True)
        self.line_more(']', tab_clear=True)
        if is_del:
            self.line_term()
        return self

    #@+node:ekr.20141010141310.19025: *5* make_local_name
    def make_local_name(self):
        self.expr.make_local_name()
        return self

    #@+node:ekr.20141010141310.19026: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = self.expr.get_hi_lineno()
        if self.subs:
            lineno = (self.subs)[-1].get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.19027: *4* class NodeTryExcept
class NodeTryExcept(Node):

    """Define exception handlers.

    """

    tag = 'TryExcept'

    #@+others
    #@+node:ekr.20141010141310.19028: *5* __init__
    def __init__(self, indent, lineno, body, handlers, else_):
        Node.__init__(self, indent, lineno)
        self.body = transform(indent + 1, lineno, body)
        self.handlers = [(transform(indent, lineno, expr), transform(indent,
                         lineno, target), transform(indent + 1, lineno,
                         suite)) for (expr, target, suite) in handlers]
        self.else_ = transform(indent + 1, lineno, else_)
        self.has_finally = False
        return 

    #@+node:ekr.20141010141310.19029: *5* put
    def put(self, can_split=False):
        if self.has_finally:
            pass
        else:
            self.line_init()
            self.line_more('try:')
            self.line_term(self.body.get_lineno() - 1)
        self.body.put()
        for (expr, target, suite) in self.handlers:
            self.line_init()
            self.line_more('except')
            if expr is None:
                pass
            else:
                self.line_more(' ')
                expr.put()
                if target is None:
                    pass
                else:
                    self.line_more(LIST_SEP, can_break_after=True)
                    target.put()
            self.line_more(':')
            self.line_term(suite.get_lineno() - 1)
            suite.put()
        if self.else_ is None:
            pass
        else:
            self.line_init()
            self.line_more('else:')
            self.line_term(self.else_.get_lineno() - 1)
            self.else_.put()
        return self

    #@+node:ekr.20141010141310.19030: *5* marshal_names
    def marshal_names(self):
        self.body.marshal_names()
        for (expr, target, suite) in self.handlers:
            suite.marshal_names()
        if self.else_ is None:
            pass
        else:
            self.else_.marshal_names()
        return self


    #@-others
#@+node:ekr.20141010141310.19031: *4* class NodeTryFinally
class NodeTryFinally(Node):

    """Force housekeeping code to execute even after an unhandled
    except is raised and before the default handling takes care of it.

    """

    tag = 'TryFinally'

    #@+others
    #@+node:ekr.20141010141310.19032: *5* __init__
    def __init__(self, indent, lineno, body, final):
        Node.__init__(self, indent, lineno)
        if isinstance(body, compiler.ast.TryExcept):
            self.body = transform(indent, lineno, body)
            self.body.has_finally = True
        else:
            self.body = transform(indent + 1, lineno, body)
        self.final = transform(indent + 1, lineno, final)
        return 

    #@+node:ekr.20141010141310.19033: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('try:')
        self.line_term(self.body.get_lineno() - 1)
        self.body.put()
        self.line_init()
        self.line_more('finally:')
        self.line_term(self.final.get_lineno() - 1)
        self.final.put()
        return self

    #@+node:ekr.20141010141310.19034: *5* marshal_names
    def marshal_names(self):
        self.body.marshal_names()
        self.final.marshal_names()
        return self


    #@-others
#@+node:ekr.20141010141310.19035: *4* class NodeTuple
class NodeTuple(Node):

    """Declaration of an immutable tuple.

    """

    tag = 'Tuple'

    #@+others
    #@+node:ekr.20141010141310.19036: *5* __init__
    def __init__(self, indent, lineno, nodes):
        Node.__init__(self, indent, lineno)
        self.nodes = [transform(indent, lineno, node) for node in nodes]
        return 

    #@+node:ekr.20141010141310.19037: *5* put
    def put(self, can_split=False, is_paren_required=True):
        # pylint: disable=arguments-differ
        if len(self.nodes) > MAX_SEPS_SERIES:
            self.line_more('(', tab_set=True)
            self.line_term()
            self.inc_margin()
            for node in self.nodes:
                self.line_init()
                node.put(can_split=True)
                self.line_more(LIST_SEP)
                self.line_term()
            if JAVA_STYLE_LIST_DEDENT:
                self.dec_margin()
                self.line_init()
            else:
                self.line_init()
                self.dec_margin()
            self.line_more(')', tab_clear=True)
        elif ((len(self.nodes) == 0) or
              is_paren_required or
              PARENTHESIZE_TUPLE_DISPLAY):
            self.line_more('(', tab_set=True)
            for node in (self.nodes)[:1]:
                node.put(can_split=True)
                self.line_more(LIST_SEP, can_split_after=True)
            for node in (self.nodes)[1:2]:
                node.put(can_split=True)
            for node in (self.nodes)[2:]:
                self.line_more(LIST_SEP, can_split_after=True)
                node.put(can_split=True)
            self.line_more(')', tab_clear=True)
        else:
            for node in (self.nodes)[:1]:
                node.put()
                self.line_more(LIST_SEP, can_break_after=True)
            for node in (self.nodes)[1:2]:
                node.put()
            for node in (self.nodes)[2:]:
                self.line_more(LIST_SEP, can_break_after=True)
                node.put()
        return self

    #@+node:ekr.20141010141310.19038: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = Node.get_hi_lineno(self)
        if self.nodes:
            lineno = (self.nodes)[-1].get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.19039: *4* class NodeUnaryAdd
class NodeUnaryAdd(NodeOpr):

    """Algebraic positive.

    """

    tag = 'UnaryAdd'

    #@+others
    #@+node:ekr.20141010141310.19040: *5* __init__
    def __init__(self, indent, lineno, expr):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        return 

    #@+node:ekr.20141010141310.19041: *5* put
    def put(self, can_split=False):
        self.line_more('+')
        self.put_expr(self.expr, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.19042: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.19043: *4* class NodeUnarySub
class NodeUnarySub(NodeOpr):

    """Algebraic negative.

    """

    tag = 'UnarySub'

    #@+others
    #@+node:ekr.20141010141310.19044: *5* __init__
    def __init__(self, indent, lineno, expr):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        return 

    #@+node:ekr.20141010141310.19045: *5* put
    def put(self, can_split=False):
        self.line_more('-')
        self.put_expr(self.expr, can_split=can_split)
        return self

    #@+node:ekr.20141010141310.19046: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.expr.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.19047: *4* class NodeWhile
class NodeWhile(Node):

    """While loop.

    """

    tag = 'While'

    #@+others
    #@+node:ekr.20141010141310.19048: *5* __init__
    def __init__(self, indent, lineno, test, body, else_):
        Node.__init__(self, indent, lineno)
        self.test = transform(indent, lineno, test)
        self.body = transform(indent + 1, lineno, body)
        self.else_ = transform(indent + 1, lineno, else_)
        return 

    #@+node:ekr.20141010141310.19049: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('while ')
        self.test.put(can_split=can_split)
        self.line_more(':')
        self.line_term(self.body.get_lineno() - 1)
        self.body.put()
        if self.else_ is None:
            pass
        else:
            self.line_init()
            self.line_more('else:')
            self.line_term(self.else_.get_lineno() - 1)
            self.else_.put()
        return self

    #@+node:ekr.20141010141310.19050: *5* marshal_names
    def marshal_names(self):
        self.body.marshal_names()
        if self.else_ is None:
            pass
        else:
            self.else_.marshal_names()
        return 

    #@+node:ekr.20141010141310.19051: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.test.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.19052: *4* class NodeWith
class NodeWith(Node):

    """Context manager.

    """

    tag = 'With'

    #@+others
    #@+node:ekr.20141010141310.19053: *5* __init__
    def __init__(self, indent, lineno, expr, vars, body):
        Node.__init__(self, indent, lineno)
        self.expr = transform(indent, lineno, expr)
        self.vars = transform(indent, lineno, vars)
        self.body = transform(indent + 1, lineno, body)
        return 

    #@+node:ekr.20141010141310.19054: *5* put
    def put(self, can_split=False):
        self.line_init()
        self.line_more('with ')
        self.expr.put(can_split=can_split)
        if self.vars is None:
            pass
        else:
            self.line_more(' as ', can_break_after=True)
            self.vars.put(can_split=can_split)
        self.line_more(':')
        self.line_term(self.body.get_lineno() - 1)
        self.body.put()
        return self

    #@+node:ekr.20141010141310.19055: *5* marshal_names
    def marshal_names(self):
        if self.vars is None:
            pass
        else:
            self.vars.make_local_name()
        self.body.marshal_names()
        return self

    #@+node:ekr.20141010141310.19056: *5* get_hi_lineno
    def get_hi_lineno(self):
        lineno = self.expr.get_hi_lineno()
        if self.vars is None:
            pass
        else:
            lineno = self.vars.get_hi_lineno()
        return lineno


    #@-others
#@+node:ekr.20141010141310.19057: *4* class NodeYield
class NodeYield(Node):

    """Yield a generator value.

    """

    tag = 'Yield'

    #@+others
    #@+node:ekr.20141010141310.19058: *5* __init__
    def __init__(self, indent, lineno, value):
        Node.__init__(self, indent, lineno)
        self.value = transform(indent, lineno, value)
        return

    #@+node:ekr.20141010141310.19059: *5* put
    def put(self, can_split=False):
        self.line_more('yield ')
        self.value.put(can_split=can_split)
        return self

    #@+node:ekr.20141010141310.19060: *5* get_hi_lineno
    def get_hi_lineno(self):
        return self.value.get_hi_lineno()


    #@-others
#@+node:ekr.20141010141310.19067: ** main
def main():
    if DEBUG:
        print 'Begin doctests.'
        doctest.testmod()
        print '  End doctests.'
    if len(sys.argv) > 1:
        file_in = sys.argv[1]
    else:
        file_in = '-'
    if file_in in ['-']:
        file_in = sys.stdin
    if len(sys.argv) > 2:
        file_out = sys.argv[2]
    else:
        file_out = '-'
    if file_out in ['-']:
        file_out = sys.stdout
    tidy_up(file_in, file_out)
#@+node:ekr.20141010141310.19062: ** tidy_up & helpers
def tidy_up(file_in=sys.stdin, file_out=sys.stdout, is_module=True, leo_c=None):

    """Clean up, regularize, and reformat the text of a Python script.

    File_in is a file name or a file-like object with a *read* method,
    which contains the input script.

    File_out is a file name or a file-like object with a *write*
    method to contain the output script.

    """

    global INPUT, OUTPUT, COMMENTS, NAME_SPACE, INPUT_CODING
    set_prefs(leo_c)
    INPUT = InputUnit(file_in)
    OUTPUT = OutputUnit(file_out)
    COMMENTS = Comments(is_module)
    NAME_SPACE = NameSpace()
    module = compiler.parse(str(INPUT))
    module = transform(indent=0, lineno=0, node=module)
    INPUT_CODING = INPUT.coding
    del INPUT
    module.push_scope().marshal_names().put().pop_scope()
    COMMENTS.merge(fin=True)
    OUTPUT.close()
#@+node:ekr.20141010141310.19070: *3* set_prefs
def set_prefs(c):
    '''Set preferences from Leo configuration, if possible.'''
    trace = False and not g.unitTesting
    global ADD_BLANK_LINES_AROUND_COMMENTS
    global DOUBLE_QUOTED_STRINGS
    global KEEP_BLANK_LINES
    global LEFTJUST_DOC_STRINGS
    global MAX_LINES_BEFORE_SPLIT_LIT
    
    global JAVA_STYLE_LIST_DEDENT
    global KEEP_UNASSIGNED_CONSTANTS
    global OVERRIDE_NEWLINE
    global PARENTHESIZE_TUPLE_DISPLAY

    if not c:
        return
    ADD_BLANK_LINES_AROUND_COMMENTS = c.config.getBool(
        'tidy_add_blank_lines_around_comments',default=True)
    DOUBLE_QUOTED_STRINGS = c.config.getBool(
        'tidy_double_quoted_strings',default=False)
    KEEP_BLANK_LINES = c.config.getBool(
        'tidy_keep_blank_lines',default=True)
    LEFTJUST_DOC_STRINGS = c.config.getBool(
        'tidy_left_adjust_docstrings',default=False)
    MAX_LINES_BEFORE_SPLIT_LIT = c.config.getInt(
        'tidy_lines_before_split_lit') or 2
    # 1.23 settings.
    JAVA_STYLE_LIST_DEDENT = c.config.getBool(
        'tidy_java_style_list_dedent',default=True)
    KEEP_UNASSIGNED_CONSTANTS = c.config.getBool(
        'tidy_keep_unassigned_constants',default=False)
    PARENTHESIZE_TUPLE_DISPLAY = c.config.getBool(
        'tidy_parenthesized_tuple_display',default= True)
    if trace:
        g.trace('tidy_add_blank_lines_around_comments',ADD_BLANK_LINES_AROUND_COMMENTS)
        g.trace('tidy_keep_blank_lines',KEEP_BLANK_LINES)
#@+node:ekr.20141010141310.18696: *3* transform
def transform(indent, lineno, node):
    """Convert the nodes in the abstract syntax tree returned by the
    *compiler* module to objects with *put* methods.

    The kinds of nodes are a Python Version Dependency.

    """

    def isinstance_(node, class_name):
        """Safe check against name of a node class rather than the
        class itself, which may or may not be supported at the current
        Python version.

        """

        class_ = getattr(compiler.ast, class_name, None)
        if class_ is None:
            result = False
        else:
            result = isinstance(node, class_)
        return result

    if isinstance_(node, 'Node') and node.lineno is not None:
        lineno = node.lineno
    if isinstance_(node, 'Add'):
        result = NodeAdd(indent, lineno, node.left, node.right)
    elif isinstance_(node, 'And'):
        result = NodeAnd(indent, lineno, node.nodes)
    elif isinstance_(node, 'AssAttr'):
        result = NodeAsgAttr(indent, lineno, node.expr, node.attrname, 
                             node.flags)
    elif isinstance_(node, 'AssList'):
        result = NodeAsgList(indent, lineno, node.nodes)
    elif isinstance_(node, 'AssName'):
        result = NodeAsgName(indent, lineno, node.name, node.flags)
    elif isinstance_(node, 'AssTuple'):
        result = NodeAsgTuple(indent, lineno, node.nodes)
    elif isinstance_(node, 'Assert'):
        result = NodeAssert(indent, lineno, node.test, node.fail)
    elif isinstance_(node, 'Assign'):
        result = NodeAssign(indent, lineno, node.nodes, node.expr)
    elif isinstance_(node, 'AugAssign'):
        result = NodeAugAssign(indent, lineno, node.node, node.op, node.expr)
    elif isinstance_(node, 'Backquote'):
        result = NodeBackquote(indent, lineno, node.expr)
    elif isinstance_(node, 'Bitand'):
        result = NodeBitAnd(indent, lineno, node.nodes)
    elif isinstance_(node, 'Bitor'):
        result = NodeBitOr(indent, lineno, node.nodes)
    elif isinstance_(node, 'Bitxor'):
        result = NodeBitXor(indent, lineno, node.nodes)
    elif isinstance_(node, 'Break'):
        result = NodeBreak(indent, lineno)
    elif isinstance_(node, 'CallFunc'):
        result = NodeCallFunc(indent, lineno, node.node, node.args, node.star_args, 
                              node.dstar_args)
    elif isinstance_(node, 'Class'):
        result = NodeClass(indent, lineno, node.name, node.bases, node.doc, 
                           node.code)
    elif isinstance_(node, 'Compare'):
        result = NodeCompare(indent, lineno, node.expr, node.ops)
    elif isinstance_(node, 'Const'):
        result = NodeConst(indent, lineno, node.value)
    elif isinstance_(node, 'Continue'):
        result = NodeContinue(indent, lineno)
    elif isinstance_(node, 'Decorators'):
        result = NodeDecorators(indent, lineno, node.nodes)
    elif isinstance_(node, 'Dict'):
        result = NodeDict(indent, lineno, node.items)
    elif isinstance_(node, 'Discard'):
        result = NodeDiscard(indent, lineno, node.expr)
    elif isinstance_(node, 'Div'):
        result = NodeDiv(indent, lineno, node.left, node.right)
    elif isinstance_(node, 'Ellipsis'):
        result = NodeEllipsis(indent, lineno)
    elif isinstance_(node, 'Exec'):
        result = NodeExec(indent, lineno, node.expr, node.locals, node.globals)
    elif isinstance_(node, 'FloorDiv'):
        result = NodeFloorDiv(indent, lineno, node.left, node.right)
    elif isinstance_(node, 'For'):
        result = NodeFor(indent, lineno, node.assign, node.list, node.body,
                         node.else_)
    elif isinstance_(node, 'From'):
        result = NodeFrom(indent, lineno, node.modname, node.names)
    elif isinstance_(node, 'Function'):
        result = NodeFunction(
            indent,
            lineno,
            getattr(node, 'decorators', None),
            node.name,
            node.argnames,
            node.defaults,
            node.flags,
            node.doc,
            node.code,
            )
    elif isinstance_(node, 'GenExpr'):
        result = NodeGenExpr(indent, lineno, node.code)
    elif isinstance_(node, 'GenExprFor'):
        result = NodeGenExprFor(indent, lineno, node.assign, node.iter,
                                node.ifs)
    elif isinstance_(node, 'GenExprIf'):
        result = NodeGenExprIf(indent, lineno, node.test)
    elif isinstance_(node, 'GenExprInner'):
        result = NodeGenExprInner(indent, lineno, node.expr, node.quals)
    elif isinstance_(node, 'Getattr'):
        result = NodeGetAttr(indent, lineno, node.expr, node.attrname)
    elif isinstance_(node, 'Global'):
        result = NodeGlobal(indent, lineno, node.names)
    elif isinstance_(node, 'If'):
        result = NodeIf(indent, lineno, node.tests, node.else_)
    elif isinstance_(node, 'IfExp'):
        result = NodeIfExp(indent, lineno, node.test, node.then, node.else_)
    elif isinstance_(node, 'Import'):
        result = NodeImport(indent, lineno, node.names)
    elif isinstance_(node, 'Invert'):
        result = NodeInvert(indent, lineno, node.expr)
    elif isinstance_(node, 'Keyword'):
        result = NodeKeyword(indent, lineno, node.name, node.expr)
    elif isinstance_(node, 'Lambda'):
        result = NodeLambda(indent, lineno, node.argnames, node.defaults,
                            node.flags, node.code)
    elif isinstance_(node, 'LeftShift'):
        result = NodeLeftShift(indent, lineno, node.left, node.right)
    elif isinstance_(node, 'List'):
        result = NodeList(indent, lineno, node.nodes)
    elif isinstance_(node, 'ListComp'):
        result = NodeListComp(indent, lineno, node.expr, node.quals)
    elif isinstance_(node, 'ListCompFor'):
        result = NodeListCompFor(indent, lineno, node.assign, node.list,
                                 node.ifs)
    elif isinstance_(node, 'ListCompIf'):
        result = NodeListCompIf(indent, lineno, node.test)
    elif isinstance_(node, 'Mod'):
        result = NodeMod(indent, lineno, node.left, node.right)
    elif isinstance_(node, 'Module'):
        result = NodeModule(indent, lineno, node.doc, node.node)
    elif isinstance_(node, 'Mul'):
        result = NodeMul(indent, lineno, node.left, node.right)
    elif isinstance_(node, 'Name'):
        result = NodeName(indent, lineno, node.name)
    elif isinstance_(node, 'Not'):
        result = NodeNot(indent, lineno, node.expr)
    elif isinstance_(node, 'Or'):
        result = NodeOr(indent, lineno, node.nodes)
    elif isinstance_(node, 'Pass'):
        result = NodePass(indent, lineno)
    elif isinstance_(node, 'Power'):
        result = NodePower(indent, lineno, node.left, node.right)
    elif isinstance_(node, 'Print'):
        result = NodePrint(indent, lineno, node.nodes, node.dest)
    elif isinstance_(node, 'Printnl'):
        result = NodePrintnl(indent, lineno, node.nodes, node.dest)
    elif isinstance_(node, 'Raise'):
        result = NodeRaise(indent, lineno, node.expr1, node.expr2, node.expr3)
    elif isinstance_(node, 'Return'):
        result = NodeReturn(indent, lineno, node.value)
    elif isinstance_(node, 'RightShift'):
        result = NodeRightShift(indent, lineno, node.left, node.right)
    elif isinstance_(node, 'Slice'):
        result = NodeSlice(indent, lineno, node.expr, node.flags, node.lower,
                           node.upper)
    elif isinstance_(node, 'Sliceobj'):
        result = NodeSliceobj(indent, lineno, node.nodes)
    elif isinstance_(node, 'Stmt'):
        result = NodeStmt(indent, lineno, node.nodes)
    elif isinstance_(node, 'Sub'):
        result = NodeSub(indent, lineno, node.left, node.right)
    elif isinstance_(node, 'Subscript'):
        result = NodeSubscript(indent, lineno, node.expr, node.flags,
                               node.subs)
    elif isinstance_(node, 'TryExcept'):
        result = NodeTryExcept(indent, lineno, node.body, node.handlers,
                               node.else_)
    elif isinstance_(node, 'TryFinally'):
        result = NodeTryFinally(indent, lineno, node.body, node.final)
    elif isinstance_(node, 'Tuple'):
        result = NodeTuple(indent, lineno, node.nodes)
    elif isinstance_(node, 'UnaryAdd'):
        result = NodeUnaryAdd(indent, lineno, node.expr)
    elif isinstance_(node, 'UnarySub'):
        result = NodeUnarySub(indent, lineno, node.expr)
    elif isinstance_(node, 'While'):
        result = NodeWhile(indent, lineno, node.test, node.body, node.else_)
    elif isinstance_(node, 'With'):
        result = NodeWith(indent, lineno, node.expr, node.vars, node.body)
    elif isinstance_(node, 'Yield'):
        result = NodeYield(indent, lineno, node.value)
    elif isinstance(node, basestring):
        result = NodeStr(indent, lineno, node)
    elif isinstance(node, int):
        result = NodeInt(indent, lineno, node)
    else:
        result = node
    return result


#@-others
#@+<< operator precedence >>
#@+node:ekr.20141010141310.19061: ** << operator precedence >>
# The abstract syntax tree returns the nodes of arithmetic and logical
# expressions in the correct order for evaluation, but, to reconstruct
# the specifying code in general and to output it correctly, we need
# to insert parentheses to enforce the correct order.

# This is a Python Version Dependency.

OPERATOR_PRECEDENCE = [
    (NodeIfExp, ),
    (NodeLambda, ),
    (NodeOr, ),
    (NodeAnd, ),
    (NodeNot, ),
    (NodeCompare, ),
    (NodeBitOr, ),
    (NodeBitXor, ),
    (NodeBitAnd, ),
    (NodeLeftShift, NodeRightShift),
    (NodeAdd, NodeSub),
    (NodeMul, NodeDiv, NodeFloorDiv, NodeMod),
    (NodeUnaryAdd, NodeUnarySub, NodeInvert, ),
    (NodePower, ),
    (NodeAsgAttr, NodeGetAttr),
    (NodeSubscript, ),
    (NodeSlice, ),
    (NodeCallFunc, ),
    (NodeTuple, ),
    (NodeList, ),
    (NodeDict, ),
    (NodeBackquote, ),
    ]
OPERATORS = []
OPERATOR_TRUMPS = {}
OPERATOR_LEVEL = {}
for LEVEL in OPERATOR_PRECEDENCE:
    for OPERATOR in LEVEL:
        OPERATOR_LEVEL[OPERATOR] = LEVEL
        OPERATOR_TRUMPS[OPERATOR] = OPERATORS[:]  # a static copy.
    OPERATORS.extend(LEVEL)


#@-<< operator precedence >>
if __name__ == "__main__":
    main()
#@-leo
